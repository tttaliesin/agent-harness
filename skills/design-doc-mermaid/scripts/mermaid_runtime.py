#!/usr/bin/env python3
"""Local Mermaid rendering with staged output, occurrence-aware extraction, and typed failures."""
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


class DiagramError(Exception):
    def __init__(self, code, message):
        self.code = code
        super().__init__(message)


@dataclass(frozen=True)
class Block:
    start: int
    end: int
    content: str
    index: int


def extract_blocks(text):
    """Read top-level CommonMark fences; never mistake a nested example for a diagram.

    Containers (blockquote/list indentation) are not transformed by this helper.
    """
    blocks = []
    opened = None
    offset = 0
    fence = re.compile(r'^( {0,3})(`{3,}|~{3,})([^\r\n]*)\r?\n?$')
    for line in text.splitlines(keepends=True):
        if opened:
            char, length, start, body, is_mermaid = opened
            close = re.match(r'^ {0,3}' + re.escape(char) + '{' + str(length) + r',}[ \t]*(?:\r?\n)?$', line)
            if close:
                if is_mermaid:
                    blocks.append(Block(start, offset + len(line), text[body:offset], len(blocks) + 1))
                opened = None
        else:
            match = fence.match(line)
            if match:
                marker, info = match[2], match[3].strip()
                if marker[0] == '`' and '`' in info:
                    offset += len(line)
                    continue
                if info == 'mermaid' and match[1]:
                    raise DiagramError('INPUT_ERROR', 'Indented Mermaid fences require a container-aware parser; no conversion performed')
                opened = (marker[0], len(marker), offset, offset + len(line), info == 'mermaid')
        offset += len(line)
    if opened and opened[-1]:
        raise DiagramError('INPUT_ERROR', 'Unclosed top-level Mermaid fence')
    return blocks


def configured_tools(mmdc=None, puppeteer_config=None):
    record = {}
    config_home = Path(os.environ.get('XDG_CONFIG_HOME', str(Path.home() / '.config')))
    config = config_home / 'agent-harness/mermaid-runtime.json'
    if not config.exists():
        config = config_home / 'developer-skills/mermaid-runtime.json'  # Existing installations
    if config.exists():
        try:
            record = json.loads(config.read_text())
        except (ValueError, OSError) as exc:
            raise DiagramError('CONFIG_ERROR', str(exc)) from exc
    executable = mmdc or os.environ.get('DESIGN_DOC_MERMAID_MMDC') or shutil.which('mmdc') or record.get('mmdc')
    if not executable or not shutil.which(str(executable)):
        raise DiagramError('TOOL_MISSING', 'mmdc is unavailable; use an existing or explicitly authorized pinned runtime')
    browser_config = puppeteer_config or record.get('puppeteer_config')
    return str(executable), browser_config


def failure_code(stderr):
    value = stderr.lower()
    if any(x in value for x in ['failed to launch', 'could not find chrome', 'no usable sandbox', 'browser process', 'chrome-headless-shell']):
        return 'BROWSER_ERROR'
    if any(x in value for x in ['parse error', 'syntax error', 'unknown diagram', 'no diagram type detected']):
        return 'SYNTAX_ERROR'
    return 'RENDER_ERROR'


def check_destination(path, overwrite=False):
    path = Path(path)
    if path.is_symlink():
        raise DiagramError('OUTPUT_CONFLICT', f'Refusing symlink output: {path}')
    if path.exists() and (not path.is_file() or not overwrite):
        raise DiagramError('OUTPUT_CONFLICT', f'Existing output requires scoped overwrite: {path}')


def publish(staged, destination, overwrite=False):
    """Replace one owned output atomically, or create it without clobbering a racer."""
    staged, destination = Path(staged), Path(destination)
    check_destination(destination, overwrite)
    if overwrite:
        os.replace(staged, destination)
    else:
        try:
            os.link(staged, destination)
        except FileExistsError as exc:
            raise DiagramError('OUTPUT_CONFLICT', str(destination)) from exc
        staged.unlink()


def render(input_path, output_path, *, mmdc=None, overwrite=False, puppeteer_config=None, timeout=60, background="white", theme="default"):
    src, out = Path(input_path), Path(output_path)
    if src.resolve() == out.resolve():
        raise DiagramError('OUTPUT_CONFLICT', 'Input and output must be distinct')
    if out.suffix.lower() not in {'.svg', '.png', '.pdf'}:
        raise DiagramError('INPUT_ERROR', 'Output must be SVG, PNG, or PDF')
    check_destination(out, overwrite)
    executable, browser_config = configured_tools(mmdc, puppeteer_config)
    if not src.is_file():
        raise DiagramError('INPUT_ERROR', f'Missing source: {src}')
    out.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='.mermaid-render-', dir=out.parent) as temp:
        source = Path(temp) / 'source.mmd'
        source.write_bytes(src.read_bytes())
        staged = Path(temp) / ('artifact' + out.suffix.lower())
        cmd = [executable, '-i', str(source), '-o', str(staged), '-b', background, '-t', theme]
        if browser_config:
            cmd += ['-p', str(browser_config)]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        except FileNotFoundError as exc:
            raise DiagramError('TOOL_MISSING', str(exc)) from exc
        except subprocess.TimeoutExpired as exc:
            raise DiagramError('TIMEOUT', f'Render exceeded {timeout} seconds') from exc
        if result.returncode:
            diagnostic = result.stderr.strip() or result.stdout.strip() or 'Renderer failed'
            raise DiagramError(failure_code(diagnostic), diagnostic)
        if not staged.is_file() or staged.stat().st_size == 0:
            raise DiagramError('OUTPUT_ERROR', 'Renderer returned no nonempty artifact')
        artifact_hash = hashlib.sha256(staged.read_bytes()).hexdigest()
        source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
        publish(staged, out, overwrite)
    return {'source_sha256': source_hash, 'artifact_sha256': artifact_hash, 'output': str(out),
            'rendered': True, 'semantic_review': 'not_verified', 'viewer_review': 'not_verified'}


def convert_markdown(input_path, output_path, image_dir, *, mmdc=None, overwrite=False,
                     puppeteer_config=None, image_format='svg'):
    """Render all supported blocks before publishing any replacement Markdown.

    This writes a review candidate; caller still owns documentation approval.
    """
    src, out, images = Path(input_path), Path(output_path), Path(image_dir)
    if src.resolve() == out.resolve():
        raise DiagramError('OUTPUT_CONFLICT', 'Write a separate review candidate; do not replace source Markdown')
    if image_format not in {'svg', 'png', 'pdf'}:
        raise DiagramError('INPUT_ERROR', 'Unsupported image format')
    check_destination(out, overwrite)
    content = src.read_bytes().decode('utf-8')
    blocks = extract_blocks(content)
    if not blocks:
        raise DiagramError('INPUT_ERROR', 'No supported top-level Mermaid blocks found; containers are not transformed')
    # Stage the whole batch before publishing; errors leave old document/images intact.
    out.parent.mkdir(parents=True, exist_ok=True)
    created = []
    with tempfile.TemporaryDirectory(prefix='.mermaid-batch-', dir=out.parent) as temp:
        stage = Path(temp)
        prepared = []
        for block in blocks:
            mmd = stage / f'{block.index}.mmd';mmd.write_text(block.content, encoding='utf-8')
            artifact = stage / f'{block.index}.{image_format}'
            receipt = render(mmd, artifact, mmdc=mmdc, puppeteer_config=puppeteer_config)
            stem = f'{src.stem}-{block.index:03d}-{receipt["source_sha256"][:16]}'
            final_mmd = images / (stem + '.mmd')
            final_image = images / f'{stem}-{receipt["artifact_sha256"][:16]}.{image_format}'
            prepared.append((block, mmd, artifact, final_mmd, final_image))
        replacements = content
        for block, _, _, _, final_image in reversed(prepared):
            relative = Path(os.path.relpath(final_image, out.parent)).as_posix()
            from urllib.parse import quote
            replacements = replacements[:block.start] + f'![Diagram {block.index}]({quote(relative, safe="/")})\n' + replacements[block.end:]
        candidate = stage / 'candidate.md';candidate.write_bytes(replacements.encode('utf-8'))
        images.mkdir(parents=True, exist_ok=True)
        # Check every destination before the first publish; immutable assets are never overwritten.
        for _, mmd, artifact, final_mmd, final_image in prepared:
            for source, target in [(mmd, final_mmd), (artifact, final_image)]:
                if target.is_symlink() or (target.exists() and (not target.is_file() or target.read_bytes() != source.read_bytes())):
                    raise DiagramError('OUTPUT_CONFLICT', f'Conflicting immutable asset: {target}')
        try:
            for _, mmd, artifact, final_mmd, final_image in prepared:
                for source, target in [(mmd, final_mmd), (artifact, final_image)]:
                    if not target.exists():
                        # Same-directory staging supports different filesystems for image_dir.
                        with tempfile.NamedTemporaryFile(dir=images, prefix='.mermaid-asset-', delete=False) as handle:
                            staged = Path(handle.name);handle.write(source.read_bytes())
                        try:
                            publish(staged, target)
                            created.append((target, hashlib.sha256(source.read_bytes()).hexdigest()))
                        finally:
                            staged.unlink(missing_ok=True)
            publish(candidate, out, overwrite)
        except Exception:
            for target, digest in created:
                if not target.is_symlink() and target.is_file() and hashlib.sha256(target.read_bytes()).hexdigest() == digest:
                    target.unlink()
            raise
    return {'output': str(out), 'images': [str(x[4]) for x in prepared], 'count': len(blocks),
            'coverage': 'top-level fences only', 'approval': 'not_attested'}
