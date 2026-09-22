# 작업 안내

작업 대상 저장소에서 시작하고, 필요한 공통 규칙만 읽는다.
실제 명령과 완료 조건은 해당 저장소의 README·AGENTS.md·검증 도구로 확인한다.

| 작업 | 작업 위치와 확인할 경계 |
| --- | --- |
| Product 기능 개발 | [Products](categories/products.md)의 책임에 맞는 저장소에서 구현·build·test |
| 공통 기능 분리 | 둘 이상의 product가 같은 interface를 실제로 필요로 할 때만 [Platforms](categories/platforms.md) 검토 |
| 개발 도구 선택·통합 | [개발 도구 기준](https://github.com/tttaliesin/agent-harness/blob/main/skills/development-tooling/references/development-tooling.md)과 [템플릿](https://github.com/tttaliesin/agent-harness/blob/main/skills/development-tooling/references/development-tooling-templates.md) 적용, 개인 설정은 `tools/`, 공통 image는 `infra/`에서 관리 |
| 기술 조사 | [Research](categories/research.md)에 질문·판단 기준·입력·재현 방법·결과 보존 |
| 원천 자료 사용 | [Data](categories/data.md)에 출처·용도·사용 조건 보존, 소비자는 자료 version 식별 |
| Product 배포 | [배포 안내](https://github.com/tttaliesin/agent-harness/blob/main/docs/ci-cd-map.md)에서 단계와 담당 skill 확인 |
| Workspace 규칙 수정 | 해당 규칙 원문 수정 후 [스킬 관리](https://github.com/tttaliesin/agent-harness/blob/main/docs/codex-skill.md)에 따라 승인된 설치본 갱신·검증 |

## 개발 환경

공통 Dev Container image와 scaffold는 `infra/`, 프로젝트의 `.devcontainer`와 image version은 해당 프로젝트가 소유한다.
공통 image는 Codex CLI를 제공하지만 Codex 로그인·설정이나 OpenCodex 연결은 개발의 필수 조건이 아니다.
기본 scaffold와 선택적인 agent 통합을 구분하고, 선택은 프로젝트의 `.devcontainer`에 명시한다.
OpenCodex network·token 또는 host의 `~/.codex` 없이도 Dev Container를 열고 build·test할 수 있어야 한다.
인증 정보·token·대화 기록·cache는 source repository에 넣지 않는다.
프로젝트별 runtime·package는 프로젝트 설정에 두고 공통 image에 올리지 않는다.

## 조사와 공통 기능

이미 구현할 기능이 분명하면 별도의 조사 저장소를 만들지 않는다.
조사 결과가 운영 서비스가 되면 구현은 해당 category에 두고 조사 근거와 연결한다.
아직 소비자가 하나뿐인 기능은 재사용을 예상해 platform으로 분리하지 않는다.
공통 interface를 제공할 때는 입력·결과·실패·호환성 계약을 정하고 소비자가 내부 구현이나 설정을 직접 소유하지 않게 한다.
학습·simulator·분석 code와 결과는 목적에 맞는 구현 저장소에 두고, 가공 결과로 원천 자료를 덮어쓰지 않는다.

## 작업 맥락과 지식 소유권

작업의 목표·범위·제약·완료 기준은 현재 요청과 해당 저장소 문서에서 확인
프로젝트별 목표·결정·상태는 해당 프로젝트, workspace 공통 정책은 Agent Harness의 소유 스킬에서 관리
여러 저장소에 걸친 지식은 실제 책임을 가진 저장소에서 관리하며 별도 governance 저장소를 필수로 요구하지 않는 기준
기존 외부 지식 자료는 작업에 필요한 경우 참고 자료로 활용하며, 별도 지식 저장소나 특정 지식 관리 skill을 일반 작업의 시작·완료 조건으로 요구하지 않는 원칙
Source·configuration·test·분석·실행 근거는 이를 생산한 저장소 또는 자료 소유 시스템에서 관리
외부 지식 자료는 변경 요청이 있는 경우 해당 범위에서 갱신하며, 구현이나 test 결과의 변경만으로 자동 갱신하지 않는 원칙

## 규칙 변경

규칙이 바꿀 대상과 동작을 먼저 확인하고, 해당 원문과 이를 참조하는 안내·스킬을 함께 갱신한다.
안내 문서에 상세 정책을 다시 쓰거나 같은 규칙을 여러 문서가 소유하게 하지 않는다.
특정 제품 기능이나 도구 실행 방법은 그 구현 저장소에서 관리한다.
