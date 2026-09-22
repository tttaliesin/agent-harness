# `tools/` 운영 규칙

이 문서는 `tools/`에 두는 개발·운영 도구의 이상적인 역할을 정한다. 여기서는 Codex 설정과
OpenCodex를 명문화한다.

## `tools/`의 기준

`tools/`에는 개발자나 운영자가 필요할 때 독립적으로 실행하거나 설정하는 도구를 둔다. 이 도구는
product 기능, product 배포, 또는 공통 runtime 자체를 제공하지 않는다.

## Coding-agent skill package

여러 작업에서 개발자의 작성·검토·진단을 돕는 범용 coding-agent skill package는 `tools/`에 둔다.
`SKILL.md`, harness별 metadata, 참고 자료와 같은 package 구성은 함께 version control할 수 있다.
범용 [Markdown authoring](https://github.com/tttaliesin/agent-harness/tree/main/skills/markdown-authoring)과 [GitHub operations](https://github.com/tttaliesin/agent-harness/tree/main/skills/github-operations) 절차는 Agent Harness가 소유

공통 Harness는 기존 스킬·정책과 부족한 실행 지원 코드를 Agent Harness 한 저장소에서 관리
Workspace의 소유권·승인·trust 정책과 범용 GitHub 작업 절차는 같은 패키지 안에서 각 소유 스킬로 구분
특정 시스템의 운영 계약을 수행하는 스킬은 해당 구현 저장소가 소유
스킬 안의 보조 scripts와 기존 명령을 재사용하고 별도 Harness 계층에서 같은 절차를 재작성하지 않는 기준

## Codex 설정

Codex 설정은 개발자가 Codex를 사용할 때 적용하는 도구 설정이다. 공통 Dev Container image는
Codex CLI를 제공하지만, Codex 설정을 사용하거나 로그인하는 일은 product 개발의 필수 조건이
아니다.

설정 repository에는 version control할 설정만 둔다. 인증 정보, token, 대화 기록, cache와 같은
개인 상태는 repository에 두지 않는다.

## OpenCodex

OpenCodex는 Codex와 같은 coding-agent client가 선택해 연결하는 개발 도구다. OpenCodex는
client가 사용할 provider 연결과 인증 token 전달 방식을 제공한다.

OpenCodex 연결은 선택 사항이다. product의 Dev Container는 OpenCodex가 실행되지 않았거나
token이 없어도 열리고 build·test할 수 있어야 한다.

## Product와 연결하는 방법

product repository는 자신의 `.devcontainer`에서 Codex 설정 사용 또는 OpenCodex 연결을 선택해
명시한다. product는 OpenCodex나 Codex 설정의 source directory를 직접 참조하지 않는다.

`infra/`는 Dev Container image와 scaffold를 제공한다. `tools/`는 Codex 설정, OpenCodex,
범용 coding-agent skill package를 제공한다. 이 경계는 실제 directory를 옮기기 전에도 적용한다.

## 공통 개발 도구 기준과의 관계

저장소의 runtime·package manager·task 진입점은 [개발 도구 기준](https://github.com/tttaliesin/agent-harness/blob/main/skills/development-tooling/references/development-tooling.md)에 따라 선택한다.
공통 채택 정책은 이 패키지의 development-tooling이 소유하며 실제 Dev Container image·호스트 구현은 infra 소유
같은 정책 본문과 image 구현을 패키지와 infra 양쪽에 복제하지 않는 기준
