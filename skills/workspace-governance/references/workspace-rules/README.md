# Workspace Rules

Workspace의 저장소 분류, 공통 작업 규칙과 이를 전달하는 coding-agent skill을 관리한다.
공통 규칙·스킬은 Agent Harness의 공통 스킬 저장소에 함께 배치하며 이 경로의 `workspace-rules`는 규칙 문서 묶음 이름
실제 실행 명령과 현재 운영 상태는 해당 구현 저장소에서 확인한다.

## 필요한 문서 찾기

| 하려는 일 | 먼저 읽을 문서 |
| --- | --- |
| 작업 시작·저장소 선택 | [작업 안내](docs/use-cases.md) |
| GitHub Issue·PR·merge | [GitHub 운영 규칙](https://github.com/tttaliesin/agent-harness/blob/main/skills/github-operations/references/github-operations.md) |
| 개발 도구 선택·템플릿 적용 | [개발 도구 기준](https://github.com/tttaliesin/agent-harness/blob/main/skills/development-tooling/references/development-tooling.md) |
| Markdown 작성·검증 | [Markdown 규칙](https://github.com/tttaliesin/agent-harness/blob/main/skills/markdown-authoring/references/markdown-authoring-rules.md) |
| 배포 구조 파악 | [CI/CD 흐름 지도](https://github.com/tttaliesin/agent-harness/blob/main/docs/ci-cd-map.md) |
| CI/CD 구현·운영 | [Actions 규칙](https://github.com/tttaliesin/agent-harness/blob/main/skills/github-actions-workflows/references/github-actions-workflows.md) |
| 새 배포 서버 연결·회수 | [서버 운영 스킬](https://github.com/suchang-busan/deploy/blob/main/skills/target-host-management/SKILL.md) |
| 규칙·스킬 수정 및 설치 | [스킬 관리](https://github.com/tttaliesin/agent-harness/blob/main/docs/codex-skill.md) |

작업 시작·인계·추가 검증·완료 판단에는 [완료와 검증 기준](docs/completion-and-verification.md) 적용

## Category 경계

Category는 용도별 폴더이며 Git repository나 현재 저장소 목록이 아니다.
각 저장소는 자기 directory를 Git root로 사용하고, 주된 결과와 소비자를 기준으로 하나의 category에 둔다.
기술·재사용 여부·하위 directory 이름만으로 분류하지 않는다.
빈 category 때문에 저장소나 구현을 만들 필요는 없다.

| Category | 주된 책임 | 상세 규칙 |
| --- | --- | --- |
| `governance/` | 독립 소유자가 필요한 공통 지식·결정; 현재 공통 정책은 Agent Harness 소유 | [Governance](docs/categories/governance.md) |
| `products/` | 사용자·고객에게 제공하는 기능과 경험 | [Products](docs/categories/products.md) |
| `infra/` | 공통 runtime·artifact 전달·운영 환경과 배포 기반 | [Infra](docs/categories/infra.md) |
| `platforms/` | 여러 제품이 interface로 소비하는 application 서비스 | [Platforms](docs/categories/platforms.md) |
| `tools/` | 개발·운영자가 독립적으로 사용하는 도구 | [Tools](docs/categories/tools.md) |
| `research/` | 질문·실험·평가와 그 결론 | [Research](docs/categories/research.md) |
| `data/` | 재사용할 원천 자료와 출처·사용 조건 | [Data](docs/categories/data.md) |

대상 category를 정한 뒤 저장소의 Git root, README, 존재하는 AGENTS.md를 확인한다.
아직 Git root가 없으면 지정 directory와 그 안의 README·AGENTS.md를 임시 경계로 사용한다.
그 공백을 메우기 위한 category-level `index.md`는 만들지 않는다.
공통 skill은 전달하는 규칙의 소유 저장소에, 특정 정본의 운영 skill은 그 정본과 함께 둔다.
범용 개발 지원 skill은 `tools/`에 둔다.
공통 스킬은 workspace 정책·범용 개발 지침·소유 스킬의 보조 도구를 `tools/agent-harness` 한 곳에서 관리
정책 원문은 해당 소유 스킬 references에 한 번만 두며 category별 별도 정책 저장소나 상위 workspace AGENTS 생성은 불필요
