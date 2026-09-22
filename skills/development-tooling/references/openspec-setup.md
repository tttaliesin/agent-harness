# OpenSpec 제품 초기 구성

첫 연결 또는 명시적인 OpenSpec 갱신에서만 적용
기존 tracker·문서·도구·사용자 수정과 승인 범위를 먼저 확인하고 동일 결정을 다시 질문하는 절차 제외

## 기존 제품 정보 확인

1. Git root·remote·기존 AGENTS.md와 CLAUDE.md·명세·도메인 문서·ADR 위치 확인
2. 실제 package manifest·lock·Taskfile 등에서 개발·검사 명령과 실행 환경 확인
3. 기존 명령·문서 위치를 짧은 제품 AGENTS.md에 연결할 필요 판단; 공통 정책 복제 제외
4. 기존 `.agents/skills/openspec-*`의 출처·버전·직접 수정 확인 후 보존

확인한 tracker·문서 위치·명령·CLI 버전·생성 스킬·보존 여부를 기존 제품 설정 기록 또는 해당 change에 기록
새 설정 정본을 추가하지 않고 이후 작업에서 같은 입력을 찾을 수 있는 위치 사용

setup-matt-pocock-skills의 초기 구성 목적을 이 절차에서 담당
기존 CLAUDE.md 보존, tracker 선택 재질문·triage 설정 강제 생성 제외

## 일곱 workflow 생성

검증 기준 CLI: `@fission-ai/openspec@1.13.1`
제품에서 선택한 CLI 버전과 설치 경로를 사용하고 전역 최신 버전으로 자동 교체 제외
Node.js 요구 버전과 실제 CLI 버전·도움말을 먼저 확인

OpenSpec 1.13.1은 custom workflow 목록을 전역 설정에서 읽으므로 아래 작업 전용 설정 디렉터리로 범위 제한
PowerShell 예시 — 임시 환경 변수는 finally에서 복원, 생성 파일은 제품 root 아래에 배치

```powershell
$setupConfig = Join-Path ([System.IO.Path]::GetTempPath()) ([System.Guid]::NewGuid().ToString())
$priorConfig = $env:XDG_CONFIG_HOME
$priorData = $env:XDG_DATA_HOME
try {
    $env:XDG_CONFIG_HOME = $setupConfig
    $env:XDG_DATA_HOME = $setupConfig
    openspec config set profile custom
    if ($LASTEXITCODE -ne 0) { throw 'OpenSpec profile selection failed' }
    openspec config set workflows '["explore","propose","apply","update","verify","sync","archive"]'
    if ($LASTEXITCODE -ne 0) { throw 'OpenSpec workflow selection failed' }
    openspec init . --tools codex --profile custom --no-animation --no-copilot-cloud
    if ($LASTEXITCODE -ne 0) { throw 'OpenSpec initialization failed' }
} finally {
    $env:XDG_CONFIG_HOME = $priorConfig
    $env:XDG_DATA_HOME = $priorData
}
```

이 예시의 전제: 해당 제품 초기 구성 승인, 기존 생성 파일의 수정 보존 완료, 고정 CLI 실행 가능
임시 설정 경로는 출력·기록 후 소유권을 확인하여 정리
기존 제품 갱신은 먼저 같은 버전과 profile로 복사본에서 diff 확인; 강제 덮어쓰기 옵션 사용 제외
후속 `openspec update .`에도 위 try/finally 전체 적용: 새 임시 XDG 경로에서 custom profile과 일곱 workflow를 다시 설정하고 init 행만 update로 교체
환경 복원 후 격리 없이 update 실행 금지 — 기존 전역 core profile이 verify를 제거하거나 workflow 발견 결과를 사용자 전역 설정에 기록할 수 있음
갱신 전후 원래 전역 설정의 바이트 동일성과 일곱 생성 스킬 보존 확인

## 생성 이후 확인

- openspec-explore·openspec-propose·openspec-apply-change·openspec-update-change·openspec-verify-change·openspec-sync-specs·openspec-archive-change의 SKILL.md와 metadata.generatedBy 확인
- `openspec list --json`·`openspec doctor --json`으로 실제 root와 진단 확인
- 해당 제품에서 Codex의 스킬 발견·실제 요청의 선택 경로 확인
- 생성 전후 기존 문서·사용자 변경 보존과 같은 이름의 이중 공급 여부 확인
- 하나의 change에서 propose→apply/update→verify→sync/archive와 제품 검사 연결

생성 파일 존재만으로 실제 발견·구현·제품 검사 완료 판정 제외
선정 근거: [OpenSpec CLI 문서](https://github.com/Fission-AI/OpenSpec/blob/main/docs/cli.md)
