# 개발 도구 기준

새 프로젝트와 도구 전환 작업에는 **mise로 도구 버전과 작업 진입점을 통일하고, 언어별 의존성은 해당 생태계 도구로 관리하는 구성**을 기본으로 사용한다.
목표는 저장소를 바꿀 때마다 설치·실행 방법을 다시 설계하는 비용을 줄이면서 제품 기능, 독립 모듈, 연구 재현성과 운영 경계를 유지하는 것이다.
이 문서는 공통 설계의 정본이며, 개별 저장소의 실제 버전과 전환 완료 상태는 해당 저장소가 소유한다.
기존 Project의 도구 채택 기록과 repository 설정은 요구와 전환 비용을 확인할 자료이며 이 설계의 기본값을 결정하는 권위로 사용하지 않는다.

## 적용과 소유권

| 소유자 | 책임 |
| --- | --- |
| `developer-skills`의 공통 Harness | 도구 선택 기준, 실행 계약, 재사용 가능한 선언 템플릿과 적용 skill |
| 각 repository | 프로젝트 목표·결정·상태, 실제 도구 버전, 의존성 lock, 모듈별 명령, 지원 환경, 전환·검증 근거 |
| `infra/` 공통 개발 환경 | OS·system library·인증서·mise bootstrap을 제공하는 image와 Dev Container scaffold 구현 |
| 개인 환경·도구 repository | host 설치, shell·editor 연결, 개인 CLI와 설정의 lifecycle |

여기의 템플릿은 정책을 실행 가능한 저장소 선언으로 전달하는 작은 예제와 렌더러다.
공통 image·host installer·application framework scaffold를 구현하는 별도 도구 플랫폼으로 확장하지 않는다.
다른 저장소의 설정 변경, 전역 도구 제거, CI·배포 실행은 해당 작업의 범위와 owning skill을 따른다.

## Codex Desktop 공통 Harness 적용

사용자가 공통 Harness 구축을 선택한 저장소는 개발자·에이전트·Lefthook·CI의 공통 명령 진입점으로 `just` 사용
일반 저장소의 mise tasks 기본값에 대한 명시적 적용 예외이며, 실제 전환 대상과 완료 상태는 각 저장소에서 기록
기존 runtime 관리자·언어 package manager·native 명령은 유지하고 `just`에서 연결
같은 검사를 just·mise·Taskfile·CI에 각각 재정의하지 않고 기존 실행 정의 한 곳으로 위임
이 정책 선언만으로 just 설치·제품 명령·CI 전환 완료를 의미하지 않는 기준

## 기본 구성

| 책임 | 기본 도구 | 선택 이유와 경계 |
| --- | --- | --- |
| 개발 runtime·CLI 버전 | mise | 다언어 저장소에서 설치·선택·실행 방식을 통일하고 저장소별 선언 제공 |
| 개발 명령 진입점 | mise tasks | 이미 필요한 mise 안에서 명령을 제공하여 별도 task runner 설치·문법 감소 |
| Python interpreter | mise의 Python backend | uv와 버전 선택을 중복하지 않고 명시한 interpreter 사용 |
| Python dependency·venv·package build | uv, `pyproject.toml`, `uv.lock` | `.venv`와 의존성 해석·실행의 단일 소유자 |
| Node.js runtime | mise의 Node backend | fnm·nvm·Volta와 프로젝트 runtime 선택 중복 제거 |
| Node dependency·workspace | mise가 설치한 pnpm | 신규 Node 프로젝트의 공통 package manager와 workspace 기능 |
| Go compiler | mise의 Go backend | 개발·CI compiler patch 고정, `GOTOOLCHAIN=local`로 자동 compiler 전환 방지 |
| Go dependency·build·test | Go 명령, `go.mod`, `go.sum` | module 계약과 compiler 선택 책임 분리 |
| Rust toolchain·target·component | rustup, `rust-toolchain.toml` | Rust 고유 component와 target lifecycle 유지 |
| Rust dependency·build·test | Cargo, `Cargo.lock` | Rust 생태계의 표준 계약 유지 |
| OS·system library·GPU SDK | Dev Container 또는 목적에 맞는 환경 명세 | mise만으로 OS·libc·driver 재현성까지 보장하지 않음 |

## 프로필 선택

| 목적 | 적용 프로필 | 추가 계약 |
| --- | --- | --- |
| Python CLI·API·일반 분석 | Python | uv locked 실행, Ruff 기본 lint·format, pytest 기본 test |
| Node 웹·서비스·CLI | Node | pnpm, package scripts에 실제 framework 명령 유지, 기존 framework checker 우선 |
| Go 서비스·진단 도구 | Go | `go test`, `go vet`, `gofmt`, 지원 최소 버전과 개발 compiler 분리 |
| Rust CLI·평가 | Rust | rustup, Cargo, rustfmt·Clippy, 필요한 target만 설치 |
| Go·Node 등 독립 앱의 통합 | 위 프로필의 조합 | root에서 모듈별 명령 조정, 언어 중립 계약·simulator 기반 통합 test |
| 문서·정책·infra 자동화 | custom | 실제 필요한 checker만 선언, build·dev가 없으면 생략 |
| ML·GPU·과학 계산 | Python 확장 또는 환경 예외 | data·model revision, seed, driver·CUDA, 실행 인자·허용 오차 기록 |

TypeScript checker·test runner는 framework와 필요한 검증에 맞춰 선택한다.
새 Vite 계열의 단위 test는 Vitest, browser 흐름은 Playwright를 우선 검토하되 framework가 제공하는 검증을 먼저 사용한다.
서로 다른 framework의 lint 구성을 하나의 거대한 공통 설정으로 합치지 않는다.
pytest·Ruff·TypeScript·test runner처럼 프로젝트 결과에 영향을 주는 도구는 프로젝트의 개발 의존성과 lock에 둔다.
`uvx`·`npx`의 고정되지 않은 일회성 다운로드를 CI 검증의 정본으로 사용하지 않는다.

Python으로 native dependency나 GPU 환경을 충분히 표현할 수 없을 때 Pixi/Conda, OS 단위의 강한 재현성이 필요할 때 Nix를 별도 평가한다.
현재 확인한 프로젝트 목적만으로 이들을 모든 저장소에 추가하지 않는다.
새 언어는 먼저 공식 toolchain·package manager를 확인하고 이 표에 책임과 검증 방법을 추가한다.
범용 언어 선택 순위나 특정 웹 framework까지 이 규칙이 강제하지 않는다.

## 버전과 환경 계약

### 선언의 단일 소유자

`mise.toml`에는 Python·Node·Go·uv·pnpm과 필요한 CLI의 정확한 버전을 기록한다.
`latest`, `lts`, major-only selector는 탐색에만 사용하고 수용할 설정에는 해석된 버전을 남긴다.
mise 자체는 자기 자신을 설치하는 task로 관리하지 않고 bootstrap environment에서 version·artifact 검증 방법을 기록한다.
지원할 OS·architecture와 검증한 mise version도 저장소의 tooling 기록에 명시한다.

| 선언 | 의미 |
| --- | --- |
| `mise.toml` | 개발에 사용할 정확한 실행 도구 선택 |
| `mise.lock` | 지원 backend·platform에서 해석된 도구 artifact 정보 |
| `pyproject.toml#requires-python`, `package.json#engines`, `go.mod#go`, `Cargo.toml#rust-version` | source·package가 지원하는 호환성 범위 |
| `uv.lock`, `pnpm-lock.yaml`, `go.sum`, `Cargo.lock` | 각 생태계의 의존성 해석·검증 정보 |
| `rust-toolchain.toml` | rustup의 compiler·component·target 선택 |
| Dev Container image digest·환경 명세 | OS·system dependency와 bootstrap 경계 |

정확한 개발 compiler가 지원 최소 버전과 같을 필요는 없다.
library의 최소 버전 지원 주장은 해당 버전의 test로 검증하며 최신 compiler 성공으로 대신하지 않는다.
`go.sum`은 checksum 목록이며 Node·Python의 lockfile과 같은 dependency solver lock으로 설명하지 않는다.
배포하는 앱·CLI·연구 실행의 lockfile은 커밋하고, library의 호환 범위와 검증 환경 lock은 구분한다.

### 언어별 선택·실행 계약

선택한 프로필의 절만 읽고 다언어 작업이면 영향받는 프로필을 함께 적용

#### Python

실행 전 `uv lock --check`로 최신성 확인 후 `uv run --no-sync` 사용
`--locked`만 사용하면 의존성 동기화가 발생하며 `--no-sync`의 암묵적 frozen 동작만으로 lock 최신성 검사를 대체할 수 없음
Python profile은 mise가 선택한 경로를 `UV_PYTHON`으로 넘기고 `UV_PYTHON_DOWNLOADS=never`를 설정한다.
`.venv`는 uv가 생성·동기화하며 mise의 자동 venv 생성과 중복하지 않는다.
추가 `.python-version`이 필요하면 mise 선언에서 파생하고 일치 검증을 둔다.
Python version 변경 후 기존 `.venv`를 그대로 성공으로 간주하지 않고 interpreter와 native package 재구성을 확인한다.

#### Node and pnpm

선택한 pnpm major에 맞는 설정 분기를 사용하고 템플릿 지원 범위 확장 전 upstream 설정 확인
pnpm은 mise가 설치하고 Corepack을 동시에 활성화하지 않는다.
`package.json#packageManager`에는 같은 pnpm version을 기록하고 pnpm 자체 version 자동 전환은 비활성화한다.
Node `engines`는 호환 범위이며 별도 Node selector가 아니다.
Node 25부터 Corepack이 기본 배포되지 않는다는 점도 bootstrap을 단순화하는 이유다.

#### Go

`go mod download` 전후 `go.mod`·`go.sum`을 비교하고 변경 시 실패 처리
초기 lock 준비에서 필요한 checksum 변경은 검토·커밋한 뒤 다시 검증하며 변경 자체를 숨기거나 되돌려 성공으로 처리하지 않는 기준
Go profile은 `GOTOOLCHAIN=local`로 선언보다 새 compiler를 자동 다운로드하지 않는다.
`go.mod`·`go.work`가 더 새 toolchain을 요구하면 실패를 해결할 버전 변경을 검토한다.

#### Rust

mise tasks에서 rustup proxy를 호출하되 mise의 `rust` selector로 compiler 중복 선택 금지
rustup bootstrap version은 환경 제공자가 기록하고 compiler는 `rust-toolchain.toml`의 정확한 channel version으로 지정
`RUSTUP_AUTO_INSTALL=0`으로 검사 중 자동 설치를 막고 directory override와 실제 compiler 출력을 확인
Rust profile은 외부에서 상속된 `RUSTUP_TOOLCHAIN` override를 제거하고 root toolchain 파일을 사용한다.
현재 검증한 mise에서 환경값을 `false`로 지정하는 것만으로 상속값이 제거되지 않아 Rust task가 명시적으로 `unset RUSTUP_TOOLCHAIN`을 실행한다.
독립적으로 더 다른 Rust compiler가 필요한 모듈은 해당 작업의 명시적 예외로 분리한다.

### Lock과 공급망

mise lock의 적용 범위는 backend와 platform마다 다르다.
지원 대상의 lock을 생성·검토하고 `mise install --locked`를 검증한 경우 이를 CI 설치 기본으로 사용한다.
예외 backend는 정확한 version만으로 같은 보증을 주장하지 않고 image digest·artifact checksum 등 대체 근거를 기록한다.
locked 실행은 offline 실행과 다르므로 실제 cache·mirror 없이 air-gapped 지원을 주장하지 않는다.
언어 lock은 mise lock으로 대체하지 않는다.

mise 설정·task·dependency install script는 실행 가능한 코드로 검토한다.
검토한 저장소 설정만 trust하고 전체 workspace를 자동 trust하거나 trust prompt를 무조건 우회하지 않는다.
CI에서 변경 가능한 task를 실행하는 일은 해당 CI의 PR trust·credential 경계를 그대로 따른다.
개발 dependency 설치에 production secret이 필요하지 않도록 구성한다.

## 공통 실행 계약

일반 저장소에서 사람과 agent의 root 진입점은 `mise tasks`, `mise run <task>`이며, 임의 native 명령은 `mise exec -- <command>` 사용
공통 Harness 적용 저장소의 공통 진입점은 위 Codex Desktop 공통 Harness 적용 절에 따라 `just` 사용
shell activation은 개발자 편의이며 script·CI의 필수 조건이 아니다.
설치는 명시적으로 수행하고 검증 task의 도구 자동 설치는 비활성화한다.

| 명령 | 의미 | 허용하는 변경 |
| --- | --- | --- |
| `mise tasks` | 지원하는 명령 탐색 | 설치·application 변경 없음 |
| `mise run doctor` | 선택 버전·경로·전제조건 확인 | 설치·복구 없음 |
| `mise run sync` | 커밋된 lock으로 dependency 동기화 | cache·venv·dependency directory |
| `mise run lint` | format·정적 규칙 검사 | source 자동 수정 없음 |
| `mise run format` | 사용자가 선택한 source format 적용 | source 수정 |
| `mise run test` | 자동 검증 | 격리된 test output·cache |
| `mise run build` | 배포·배포판 후보 artifact 생성 | build output |
| `mise run check` | 선언된 lint·test·build의 성공을 순서대로 확인 | 위 검증의 output |
| `mise run dev:<module>` | 선택 모듈의 foreground 개발 서버 | 로컬 개발 상태 |
| `mise run test:integration` | 필요 시 simulator·로컬 service 통합 검증 | 해당 test가 소유한 자원 |

해당하지 않는 task는 생략하고 이유를 기록한다.
빈 `test`, `echo success`, `--if-present`로 필요한 검증이 통과한 것처럼 만들지 않는다.
`check`는 의존성을 설치하거나 lock을 갱신하지 않으며, 실패한 하위 명령의 exit code를 전파한다.
mise `depends`는 병렬 실행될 수 있으므로 sync → check 같은 순서는 순차 `run` 또는 명시적 task dependency로 표현한다.
CI의 필수 check에는 부정확한 `sources`·`outputs`나 remote cache hit로 검증을 건너뛰는 최적화를 기본 적용하지 않는다.

모듈별 namespace는 `lint:api`, `test:ui`처럼 동일한 동사로 구성한다.
실제 언어 명령은 package scripts·native tool·`scripts/`가 소유하고 mise는 얇게 호출한다.
복잡한 배포·rollback 로직이나 장시간 process supervisor를 task runner에 재구현하지 않는다.
`check`, `sync`, `dev`가 운영 PLC에 쓰기 요청을 보내거나 publish·deploy를 실행해서는 안 된다.
local service task는 project name·port·cleanup ownership을 정하고 전역 container cleanup을 사용하지 않는다.

## 다언어 저장소와 실행 환경

root `mise.toml`이 공통 도구 버전과 모듈 조정을 맡고 각 앱은 독립 manifest·build·test를 유지한다.
pnpm workspace는 JavaScript package 사이 실제 dependency graph가 있을 때 사용한다.
같은 repository에 있다는 이유만으로 Go·Python 앱을 Node workspace package로 감싸지 않는다.
서로 다른 Node 앱의 lock을 합칠지는 독립 배포·갱신 요구에 따라 정하고, pnpm 사용과 lock 하나 사용을 동일시하지 않는다.
`go.work`·uv workspace·Cargo workspace도 실제 언어 내 공유 요구가 있을 때 추가한다.

기본 shell profile은 Linux·WSL의 POSIX 환경이다.
macOS·Windows native·ARM64 지원은 공식 도구 지원만으로 확정하지 않고 해당 profile의 실제 검증 이후 선언한다.
Windows UI와 WSL 실행 경계, Linux working copy, native library·network 요구는 프로젝트 목적에 맞게 유지한다.
Dev Container는 동일 `mise.toml`을 소비하며 base image의 우연한 Node·Go 버전을 정본으로 삼지 않는다.
공통 image는 bootstrap·공통 OS 도구만 제공하고 프로젝트가 필요 도구를 선택한다.
개발 환경과 production image는 독립 계약이며 mise 도입이 production image에 mise를 포함해야 한다는 뜻은 아니다.
CI는 같은 명령과 version declaration을 사용하되 runner provisioning·secret·build·promotion 권한은 기존 owning skill을 따른다.

## 다른 후보의 위치

| 후보 | 기본에서 제외한 이유 | 사용하는 조건 |
| --- | --- | --- |
| just | 일반 저장소에서 mise와 task 진입점 중복 | 공통 Harness 적용 저장소의 지정 진입점 또는 mise 제약·구체적 문법 이점이 있는 환경 |
| Task | mise와 orchestration 중복 | 기존 기능의 동등 전환이 어렵거나 YAML task 생태계가 구체적으로 필요한 경우 |
| Make | 일반 개발 명령에는 file target semantics 부담 | file dependency·증분 빌드가 핵심인 build engine으로 native 유지 |
| asdf·fnm·nvm | 프로젝트 runtime selector 중복 | mise backend·OS·정책 제약이 있는 명시적 환경 예외 |
| proto·moon | 별도 toolchain·build graph 운영 비용 | 큰 모노레포의 affected build·cache 요구를 측정해 이점 확인 |
| direnv | 기본 환경 선언·활성화 기능 중복 | shell 이탈 시 환경 복구 등 별도 요구가 있고 mise와 소유권 분리 가능 |
| Nx·Turborepo·Bazel | 현재 프로젝트 목적만으로 build graph 플랫폼 필요성 부족 | 실제 graph·cache·증분 CI 비용이 단순 mise 조정을 초과 |

기존 구성이 작동한다는 사실은 전환을 생략할 영구 예외가 아니다.
반대로 통일 자체를 위해 기능·검증·호환성을 잃는 일괄 치환도 하지 않는다.
기존 runner는 전환 기간의 adapter로 유지하고, 사용자가 호출할 root 진입점은 하나로 수렴시킨다.

## 적용·전환과 수용

1. 목적·지원 환경·완료 조건과 현재 명령의 의미 확인
2. 필요한 언어 profile·도구 버전·모듈 경계 선택
3. [템플릿 사용법](development-tooling-templates.md)에 따라 새 directory에 선언 생성
4. 기존 설정과 비교하여 버전 선택·lock·명령의 소유권 통합
5. 격리된 환경에서 설치·sync·doctor·check·대표 사용자 흐름 검증
6. README·CI·Dev Container의 호출을 같은 계약으로 연결
7. 동등 동작 확인 후 중복 selector·runner와 과도기 adapter 제거

Package manager 전환은 runtime 전환과 분리해 lock graph·lifecycle script·native addon·container build·cache 변화를 검토한다.
npm에서 pnpm으로 바꾸면 dependency 선언 누락·hoisting 가정·install script 허용 정책을 확인하고 실패 원인을 무시하는 옵션으로 덮지 않는다.
Go·Node 제품의 PLC 흐름은 simulator로 확인하고, 개발 도구 변경을 근거로 운영 장비 실행 권한을 확대하지 않는다.

전환 기록에는 이전 설정 revision, 적용한 template version, source manifest·lock 변경, 제거할 중복 도구, 새 환경 검증 결과와 복구할 이전 설정을 남긴다.
개인 전역 도구는 repository 전환과 동시에 임의 삭제하지 않는다.
실패 시 이전 설정·lock·image 조합으로 복구하며 새로운 cache를 지우는 일과 source 변경을 되돌리는 일을 구분한다.

수용 근거는 fresh checkout 또는 동등하게 격리된 임시 환경의 bootstrap → install → sync → doctor → check 성공, 버전 경로 일치, 실패 전파, lock 불변성이다.
네트워크·OS·hardware 때문에 실행하지 못한 항목은 그대로 기록한다.
여러 번 도구를 선택할 필요가 없는지, 문서의 첫 실행이 성공하는지, 로컬·CI가 같은 명령을 사용하는지를 확인한다.

## 유지보수

템플릿은 revision으로 배포하고 소비 저장소는 채택한 version과 예외를 기록한다.
새 template를 다시 복사해 저장소를 덮어쓰지 않고 기존 version과 새 version의 차이를 검토해 갱신한다.
정기 dependency·runtime 보안 업데이트와 template 구조 업데이트를 구분한다.
공통 정책은 도구명·선택 기준을 유지하고 각 repository가 실제 버전 갱신과 compatibility test를 소유한다.
목표 OS 추가, backend 변경, 반복되는 환경 drift, task graph 비용 증가가 발생하면 해당 결정만 재평가한다.

선정 근거와 확인 한계는 [개발 도구 조사](https://github.com/suchang-busan/workspace-rules/blob/c8c4e6f9547e0ec9c82e9c4445be9502d48b4f6d/docs/research/development-tooling-evaluation.md), 목적별 적용 판단은 [설계 근거와 검증](https://github.com/suchang-busan/workspace-rules/blob/c8c4e6f9547e0ec9c82e9c4445be9502d48b4f6d/docs/research/development-tooling-design-evidence.md)에 기록한다.
