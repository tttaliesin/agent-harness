# 개발 도구 템플릿 사용법

[개발 도구 기준](development-tooling.md)을 저장소의 `mise.toml`과 adoption 기록으로 반복 적용하는 방법이다.
템플릿은 application source·framework scaffold·CI YAML·Dev Container image를 생성하지 않는다.
실제 프로젝트 목적에 맞는 모듈과 명령을 연결하는 tooling overlay이며 source는 `skills/development-tooling/` 안에 있다.

## 입력 선택

| 예제 | 대상 | 필요한 실제 프로젝트 파일 |
| --- | --- | --- |
| `assets/specs/python.json` | Python CLI·API·일반 분석 | `pyproject.toml`, `uv.lock`, Ruff·pytest 개발 의존성과 test |
| `assets/specs/node.json` | Node 웹·서비스 | `package.json`, `pnpm-lock.yaml`, 실제 lint·format·test·build·dev scripts |
| `assets/specs/go.json` | Go 서비스·도구 | `go.mod`, 필요한 `go.sum`, source와 test |
| `assets/specs/rust.json` | Rust CLI·평가 | `Cargo.toml`, `Cargo.lock`, source와 test, 환경에서 제공하는 rustup |
| `assets/specs/polyglot.json` | Go API와 Node UI | `apps/api`, `apps/ui`의 독립 manifest·검증 |
| `assets/specs/automation.json` | 이 규칙 저장소 같은 문서·자동화 | 기록한 Python 3 bootstrap과 해당 저장소의 실제 scripts |

예제의 숫자는 렌더링할 수 있는 고정값의 예시이며 2026-09-07의 최신·보안 권장 버전 목록이 아니다.
채택 시 지원되는 upstream release와 framework 호환 범위를 확인해 정확한 patch version으로 바꾼다.
예제의 경로·명령도 적용 대상에 맞춰 수정하고 실제로 없는 test·build는 성공하는 빈 명령으로 대신하지 않는다.
설치된 skill에서는 같은 상대 경로로 예제와 renderer를 사용할 수 있다.

## 생성

아래는 이 저장소 루트에서 실행하는 예다.
Python 3가 필요하고 외부 Python package는 사용하지 않는다.
`/tmp/tooling-spec.json`은 검토·편집할 입력이며 `/tmp/tooling-overlay`는 존재하지 않는 출력 directory여야 한다.

```bash
cp skills/development-tooling/assets/specs/polyglot.json /tmp/tooling-spec.json
```

입력의 버전·경로·명령을 확인하고 수정한 다음 렌더링한다.

```bash
python3 skills/development-tooling/scripts/render-template.py \
  /tmp/tooling-spec.json /tmp/tooling-overlay
```

Renderer는 기존 경로와 symlink를 거부하며 설치·trust·네트워크·명령 실행을 수행하지 않는다.
출력 검토 후 대상 저장소의 설정과 병합한다.
원래 저장소에 반복 실행하는 방식으로 업데이트하지 않는다.

## 입력 계약

| 필드 | 의미 |
| --- | --- |
| `schema` | 현재 `1` |
| `mise_version` | 검증·bootstrap에 사용할 정확한 mise version, 현재 template의 최소 검증 기준 `2026.8.10` |
| `tools` | 정확한 version을 가진 mise tool mapping, 쓰는 도구만 포함 |
| `modules[].name` | task namespace로 사용할 유일한 소문자 slug |
| `modules[].kind` | `python`, `node`, `go`, `rust`, `custom` |
| `modules[].path` | repository 내부의 상대 module 경로 |
| `modules[].commands` | 실제 `lint`, `format`, `test`, `build`, `dev` 중 적용할 명령의 순차 배열 |
| `rust_toolchain` | Rust profile을 사용할 때 정확한 compiler version |

custom profile은 임의 script를 연결하므로 실행 도구를 제공하는 image·bootstrap도 adoption 기록에 남긴다.
명령은 shell code이며 신뢰할 수 없는 입력을 실행하는 sandbox가 아니다.
Renderer는 profile별 syntax와 명령의 존재를 완전히 증명하지 않는다.
실제 명령 검증은 소비 저장소에서 수행한다.

루트 aggregate task는 적용 가능한 모듈만 순서대로 호출한다.
`dev`는 전체 모듈을 자동 실행하지 않고 `dev:ui`처럼 선택적으로 제공한다.
`check`는 lint → test → build 순서로 호출하고 첫 실패에서 중단한다.
입력에 없는 검증의 필요성은 adoption 시 판단하며 generator 통과를 품질 검증으로 간주하지 않는다.

## 출력 병합

| 출력 | 적용 방법 |
| --- | --- |
| `mise.toml` | 기존 runtime·task 설정과 비교해 root 실행 계약으로 병합 |
| `tooling-template.json` | template version, 입력 spec, 아직 미검증인 상태 기록 |
| `ADOPTION.md` | 검증·전환 결과를 실제 repository의 결정 기록으로 완성 |
| `gitignore.fragment` | 관련 항목을 기존 `.gitignore`에 병합 |
| `package.fragment.json` | 각 독립 pnpm root의 `package.json`에 `packageManager` 병합 |
| `pnpm-workspace.fragment.yaml` | 선택한 major용 설정을 각 독립 pnpm root의 `pnpm-workspace.yaml`에 병합 |
| `rust-toolchain.toml` | Rust profile에서 root toolchain 선택의 정본으로 사용 |

pnpm 10.6 이상 template은 `managePackageManagerVersions: false`와 `packageManagerStrictVersion: true`를 사용한다.
pnpm 11·12 template은 `pmOnFail: error`와 `runtimeOnFail: error`를 사용한다.
이외 major는 자동 생성하지 않고 upstream 문서 확인·template 검증 후 지원 범위를 확장한다.
`pnpm-workspace.yaml`이라는 파일명만으로 모든 Node 앱을 하나의 workspace dependency graph로 합치지 않는다.

모든 Rust task의 실행 전 root toolchain을 명시적으로 설치한다.
예제의 compiler version을 채택 버전으로 바꾸어 `rustup toolchain install`을 실행하고 필요한 rustfmt·Clippy·target을 제공한다.
`doctor`는 runtime path·version 관찰이며 version mismatch 자동 수정을 수행하지 않는다.
선언과 출력이 일치하는지는 adoption 검증에서 확인한다.
Rust의 directory override도 확인하며, 생성된 compiler assertion은 toolchain version 갱신 시 함께 갱신한다.
이 assertion은 선택 권한이 아닌 불일치 검증이다.
Profile은 `RUSTUP_AUTO_INSTALL=0`과 task별 환경 override 해제를 사용한다.
Python 명령은 먼저 `.venv`와 lock을 확인하고 `uv run --no-sync`로 실행하여 검증 중 dependency를 설치하지 않는다.
Go sync는 다운로드 전후 `go.mod`·`go.sum`을 비교하고 변경이 있으면 실패와 변경 파일을 남긴다.

## 설치와 실행 검증

검토한 `mise.toml`을 trust한 뒤 도구 설치, native dependency lock 생성·검토, 지원 platform의 mise lock 준비를 수행한다.
첫 lock 생성은 dependency 해석 단계이며 이후 재현 단계의 locked sync와 구분한다.
예제 overlay 자체에는 app manifest나 실제로 생성한 lock이 포함되지 않는다.

```bash
mise install
mise run sync
mise run doctor
mise run check
```

custom profile에 dependency sync가 없다면 `sync`를 생략한다.
지원 backend와 platform의 lock을 준비한 이후에는 `mise install --locked`로 설치를 검증한다.
`mise.lock` 명령의 지원 범위는 [공식 lockfile 문서](https://mise.jdx.dev/dev-tools/mise-lock.html)를 따른다.
Python의 uv 환경과 Rust toolchain도 별도로 확인한다.
개발·CI에서 lock 변경 없이 동일 명령을 수행하고 대표 제품·연구 결과를 검증해야 실제 전환이 완료된다.

## 템플릿 수정 시 확인

Renderer나 템플릿을 수정할 때 임시 출력 경로에서 변경한 profile을 생성하고 결과를 확인한다.
입력 검증이나 파일 쓰기를 변경했다면 잘못된 입력 거부와 기존 파일 보존도 확인한다.
Task 동작을 변경했다면 필요한 도구가 준비된 환경에서 실행 순서와 실패 전파를 확인한다.
실행한 확인과 미확인 범위는 작업 결과에 보고한다.
