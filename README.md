# 개발자 스킬과 공통 Harness

에이전트가 따라갈 조사·설계·검증 절차를 필요한 작업에 맞춰 불러오는 Codex 스킬 모음
버그 원인 조사, API 계약 검토, 문서 구성과 GitHub 작업처럼 반복되는 기준을 각 `SKILL.md`에 두고 프로젝트마다 다시 설명하지 않고 재사용
필요한 스킬 하나만 설치하거나 같은 저장소의 Core plugin·검증 실행기와 함께 사용 가능

공통 Harness는 이 스킬들과 정책·지원 코드가 들어 있는 한 패키지
OpenSpec 명세와 제품의 기존 테스트 명령을 연결하고, 실행한 검사·후보 코드·report를 evidence로 기록
기존 스킬의 Git·병렬 작업·디버깅 절차를 재사용하며 Core 연결만 추가

## 공통 Harness 시작

Python 3.12.14, uv 0.12.10, just 1.58.0과 Git 필요
버전 정본은 `mise.toml`이며 Linux/WSL에서는 검토한 설정을 trust한 뒤 `mise install --locked python uv just`로 명시적으로 설치
Windows에서는 같은 버전 실행 파일을 PATH에 준비

저장소 root에서 실행

```bash
just doctor
just sync
just check
```

`sync`는 dependency를 설치하고 `check`는 lock 갱신 없이 패키지·schema·실패 사례와 실제 프로세스 테스트 및 배포판 build를 수행
첫 결과는 종료 코드와 `.harness/development/reports/pytest.xml`, `dist/`에서 확인

제품 연결은 [설치·갱신](docs/harness-installation.md) → [OpenSpec 생성](docs/openspec-binding.md) → [CLI 계약](docs/harness-cli.md) 순서
예를 들어 제품 테스트가 실패하거나 report가 비어 있으면 실행 결과를 FAIL로 기록하고, 후보 코드가 바뀌면 이전 evidence를 완료 근거로 거부
실제 Allsen Adapter·Web/Python/Streaming fixture·CI/배포 연결은 후속 단계이며 [남은 연결 조건](docs/implementation/compatibility-blockers.md)에 상태 기록

[사용 사례](#사용-사례) · [빠르게 시작](#빠르게-시작) · [작업별 스킬](#스킬)

## 사용 사례

아래 내용은 각 스킬의 현재 계약을 바탕으로 한 설명용 사례이며 실제 실행 로그나 성능 비교가 아님

### 저장소 하나만 개인 계정으로 작업

회사 계정과 개인 계정이 모두 로그인된 환경에서 현재 GitHub.com HTTPS 저장소만 개인 계정에 연결하는 상황
Python 3.10 이상, GitHub CLI와 이미 로그인된 개인 계정 필요하며 세부 조건과 명령은 [multi-github-account-operate](skills/multi-github-account-operate/SKILL.md)에서 확인
`<PERSONAL_ACCOUNT>`를 실제 계정 이름으로 교체해 Codex 대화에 입력

```text
$multi-github-account-operate 이 저장소를 개인 계정 <PERSONAL_ACCOUNT>에 연결해줘
```

연결 뒤 계정 선택 범위

| 동작 | 사용하는 계정·값 |
| --- | --- |
| 이 저장소의 HTTPS Git | `<PERSONAL_ACCOUNT>` |
| 이 저장소에서 실행한 `git gh` | `<PERSONAL_ACCOUNT>` |
| 일반 `gh` | 기존 활성 계정 |
| commit 작성자 `user.name`·`user.email` | 기존 설정값 |

### 로컬에서는 통과하지만 CI에서만 실패하는 문제 수정

```text
$systematic-debugging 로컬에서는 통과하지만 CI에서 실패하는 테스트의 원인을 찾아 수정해줘
```

대표 결과

| 흐름 | 확인할 내용 |
| --- | --- |
| 오류·실행 조건 수집 | CI 실행 명령·오류 위치·최근 변경과 관련 버전·설정을 로컬 조건과 대조 |
| 재현 | 같은 명령과 입력에서 실패가 시작되는 환경 경계 확인 |
| 가설 확인 | 관찰한 차이 하나를 원인 후보로 세우고 한 변수만 바꾸는 최소 검증 |
| 수정·회귀 검사 | 확인된 원인만 수정하고 실패 재현과 관련 검사를 다시 실행해 결과 구분 |

## 빠르게 시작

Git과 Node.js/npm 준비 후 README를 바꿀 대상 프로젝트를 Codex에서 열기
다음 명령의 `--global`은 스킬을 사용자 범위에 설치해 여러 프로젝트에서 사용할 수 있게 하는 옵션

1. 터미널에서 스킬 하나 설치

   ```bash
   npx skills add tttaliesin/developer-skills --skill readme-authoring --agent codex --global --yes
   ```

2. Codex 대화에 다음 요청 입력

   ```text
   $readme-authoring 이 프로젝트 README를 처음 쓰는 개발자가 용도와 사용 결과를 이해하고 시작할 수 있게 고쳐줘
   ```

3. 기대 결과 확인

   - 실제 코드·설정·예제를 근거로 대표 입력·출력과 첫 실행 안내 제시
   - 설치·호출에서 첫 결과 확인까지 이어지는 독자 경로 구성
   - 실제 수행한 검증, 정적 확인과 남은 한계를 Codex 응답에서 구분

## 스킬

아래 작업별 목록에서 스킬을 선택하고 연결된 `SKILL.md`에서 적용 조건과 세부 규칙 확인

### 버그 조사와 코드 검토

| 스킬 | 선택할 작업 |
| --- | --- |
| [systematic-debugging](skills/systematic-debugging/SKILL.md) | 근거 수집으로 버그 원인을 찾고 수정 결과 검증 |
| [differential-review](skills/differential-review/SKILL.md) | PR·커밋·diff의 보안 위험, 변경 영향과 테스트 누락 검토 |
| [webapp-testing](skills/webapp-testing/SKILL.md) | 로컬 웹 UI의 실제 화면, 브라우저 오류와 사용자 흐름 검증 |

### 설계와 문서

| 스킬 | 선택할 작업 |
| --- | --- |
| [api-design-principles](skills/api-design-principles/SKILL.md) | HTTP API와 비동기 메시지의 호환성·검증·멱등성 설계 |
| [design-doc-mermaid](skills/design-doc-mermaid/SKILL.md) | 코드·요구사항을 구조·배포·순서·상태 Mermaid 다이어그램으로 작성·검증 |
| [markdown-authoring](skills/markdown-authoring/SKILL.md) | Markdown 문서의 구조·표·링크·코드·접근성 작성·편집·검토 |
| [readme-authoring](skills/readme-authoring/SKILL.md) | 저장소 README를 독자 목적·첫 사용·결과 확인 중심으로 작성·개편·검토 |

### 작업 분담과 GitHub

| 스킬 | 선택할 작업 |
| --- | --- |
| [parallel-worktree-development](skills/parallel-worktree-development/SKILL.md) | 독립적인 구현 조각을 여러 Git worktree에서 병렬 개발하고 로컬 결과를 통합할 때 사용 |
| [multi-github-account-operate](skills/multi-github-account-operate/SKILL.md) | 한 GitHub.com HTTPS 저장소만 지정 계정에 연결하고 전역 로그인 변경 없이 인증 분리 |
| [github-operations](skills/github-operations/SKILL.md) | Issue·브랜치·PR·merge·release의 권한, 납품과 실제 상태 검증 |

### 공통 정책과 Core 연결

| 스킬 | 선택할 작업 |
| --- | --- |
| [workspace-governance](skills/workspace-governance/SKILL.md) | 여러 저장소의 소유권·배치 판단 |
| [development-tooling](skills/development-tooling/SKILL.md) | 도구 버전·공통 명령·언어 도구 연결 |
| [github-actions-workflows](skills/github-actions-workflows/SKILL.md) | Actions와 Product CI 계약 |
| [workflow-core](plugins/workflow-core/.codex-plugin/plugin.json) | 제품 준비·구현·독립 리뷰·PR 후속 작업·인계 연결 |
| [선택 upstream](docs/upstream-selection.md) | 고정 Matt·Superpowers 스킬과 조정 근거 |

## 설치

이 저장소 root에서 기존 개발·정책 스킬만 사용자 범위로 설치
Plugin은 위 설치 문서의 Codex plugin 경로를 사용하며 같은 스킬을 두 경로에서 동시에 설치하지 않는 방식

```bash
npx skills add ./skills --skill '*' --agent codex --global
```

## 업데이트

터미널에서 설치한 스킬 이름을 지정해 업데이트

```bash
npx skills update readme-authoring --global
```

다른 스킬은 `readme-authoring`을 [작업별 스킬 이름](#스킬)으로 교체

## 라이선스

외부 스킬의 라이선스와 출처는 각 스킬 폴더의 `LICENSE.txt`와 `NOTICE.md` 참고
