# 설치·갱신·복귀

## 공통 패키지 준비

저장소의 검토한 고정 revision을 checkout한 후 README의 도구 버전 준비와 `just sync`, `just check` 실행
사용자 스킬은 이 저장소의 `skills/`에서 설치하고 plugin 스킬은 아래 native loader에서만 설치
기존 같은 이름의 설치본에 사용자 변경이 있으면 비교·백업 후 원본에 반영하고 교체

```bash
npx skills add ./skills --skill '*' --agent codex --global
codex plugin marketplace add /absolute/developer-skills
codex plugin add workflow-core@personal
codex plugin add matt-engineering@personal
codex plugin add superpowers-execution@personal
codex plugin list --json
```

Marketplace 정본은 저장소 `.agents/plugins/marketplace.json`이며 이름은 `personal`
동일 이름 marketplace가 이미 등록된 환경에서는 기존 source를 확인하고 이름 충돌을 해소한 후 진행
이 예시는 현재 선택한 로컬 repository marketplace이며 원격 공개 범위와는 별개
설치 뒤 새 task에서 스킬을 조회하여 같은 이름이 한 번씩 로딩되는지 확인

## CLI와 hook

`just sync`는 `.venv`에 `harnesskit`과 `harnesskit-codex-hook` 실행 파일 설치
Codex를 시작하는 실행 환경의 PATH에 해당 `.venv/bin` 또는 Windows `.venv/Scripts`를 포함
시작한 앱의 환경이 바뀌지 않으면 CLI 설치만으로 hook 명령이 발견되지 않을 수 있으므로 실제 native 이벤트에서 확인

Core의 `hooks/hooks.json`이 네 이벤트를 제공하며 제품 `.codex/hooks.json`에 같은 정의를 추가하지 않는 방식
설치 후 Codex `/hooks`에서 현재 명령 정의를 검토·trust해야 실행 가능
신뢰 우회 옵션이나 앱 내부 DB 편집은 설치 절차에 포함하지 않음

Hook은 제품 `harness/project.yaml`이 있는 경우에만 동작
SessionStart는 실행 명령을 안내하고, Stop은 실제 검증 context와 증거를 다시 확인하여 필요한 경우에만 제한된 재검토 요청
재진입·동일 이벤트·중단·차단·repair budget 소진은 반복 실행을 요청하지 않음
Hook의 local evidence는 CI 또는 read-only enforcement의 증거가 아님

## 제품 역할 연결

제품 root 내부에 아래 명령을 실행하며 `--template-root`는 이 패키지의 `templates/`

```bash
harnesskit --root /absolute/product sync \
  --template-root /absolute/developer-skills/templates \
  --manifest binding.json
```

Manifest에 있는 네 `.codex/agents/*.toml`만 생성하고 `harness/lock.json`에 소유 hash 기록
반복 실행은 같은 입력이면 무변경이며 사용자가 고친 대상은 충돌로 보고
OpenSpec·AGENTS·제품 실행 명령은 기존 내용을 읽고 제품 단계에서 연결
이 역할 binding만으로 제품 Adapter 또는 실제 read-only 검증 완료를 주장하지 않는 기준

## 업데이트와 복귀

1. 정확한 이전 revision과 설치 스킬 백업·제품 `harness/lock.json` 보존
2. 별도 작업 branch에서 upstream source·license·필수 참조와 실제 patch 검토
3. `python scripts/refresh-package-lock.py`로 변경 후보를 읽고 검토 후 `--write`, 이어서 `python scripts/update-bindings.py`
4. `just check`와 영향받은 제품·fixture 검증
5. 검토한 revision에서 동일 local marketplace source 확인 후 재설치
6. 기존 plugin을 수정하는 개발 갱신은 Codex의 cachebuster 도구와 `codex plugin add` 사용
7. 실패하면 이전 revision·설치본으로 복귀하고 binding conflict는 사용자 변경을 보존하여 해결

자동 `latest` 추종이나 제품 파일 강제 덮어쓰기는 없음
Web/Python/Streaming fixture가 아직 준비되지 않은 현재 단계의 갱신을 전체 제품 호환성 검증으로 표현하지 않음
