# 스킬 공급과 기존 프로젝트의 책임

## 원본과 소비

현재 통합 소스와 실행 결과의 소유 위치

| 위치 | 책임 |
| --- | --- |
| agent-harness/skills | 공통 스킬 22개와 각 소유 스킬의 구체적인 보조 도구 |
| agent-harness/provenance | 선택 upstream 원본·license·Git object·적용 patch |
| agent-harness/scripts·tests | 저장소 유지보수·candidate·보고서·미디어 helper 회귀 검사 |
| agent-harness/fixtures/openspec | 고정 CLI 1.13.1의 실제 생성·갱신·정본 반영·archive 검사 |
| agent-harness/fixtures/web-api·streaming | 실행 예제 두 개, 각각의 OpenSpec 요구와 생성 스킬 7개 |
| 사용자 또는 제품의 .agents/skills | 선택 설치한 공통 스킬과 제품에서 생성한 OpenSpec; 같은 이름의 단일 공급 |
| 제품 저장소 | 요구·소스·기존 명령·검사·제품별 지침·실제 CI |
| infra/deploy·runner | 실제 CI 인프라·배포·관측·복구 |
| workspace-rules | 정책 공급을 종료한 역사 자료 |

Codex가 스킬을 읽고 제품의 기존 명령 실행
npx skills는 선택 설치·갱신, OpenSpec CLI는 제품의 proposal·design·delta specs·tasks와 생성 스킬 관리
제품의 Taskfile·npm·Go·Python 검사 본문과 실제 제품 명세를 그대로 사용
별도 공통 runtime·제품 Adapter·binding·change YAML 계층 추가 제외

## 실제 작업의 진입점

공통 22개 중 새로 추가한 세 스킬과 기존 소유자의 연결

| 작업 | 구현 위치 | 제품에 남는 책임 |
| --- | --- | --- |
| 승인된 변경 진행·재개 | [project-workflow](../../skills/project-workflow/SKILL.md) | 현재 change·기존 승인·명세·실제 명령·전달 지점 |
| 처음 구성·OpenSpec 갱신 | [development-tooling setup](../../skills/development-tooling/references/openspec-setup.md) | 기존 tracker·CLAUDE·AGENTS·사용자 수정과 설정 보존 |
| 공식 리뷰 | [code-review](../../skills/code-review/SKILL.md), [candidate helper](../../skills/code-review/scripts/check-candidate.py) | 고정 후보·명세·제품 검사·실제 위임 권한 |
| Python 결과 판정 | [python-testing](../../skills/python-testing/SKILL.md), [JUnit 검사기](../../skills/python-testing/scripts/check-junit.py) | 실행 명령·시작 시간·exit·실제 보고서 |
| Web 탐색·회귀 | [webapp-testing](../../skills/webapp-testing/SKILL.md), [Web/API 사용법](../../fixtures/web-api/USAGE.md) | 실제 URL·계정·MCP 재현과 저장된 Test |
| 영상 단절·복구·수신 | [streaming-testing](../../skills/streaming-testing/SKILL.md), [CPU fixture](../../fixtures/streaming/README.md) | 실제 제품 forwarding·GPU·tracker와 승인된 timing 기준 |
| PR 후속·인계 | [github-operations 절차](../../skills/github-operations/references/followup-and-handoff.md) | 실제 PR/head·처리 이벤트·쓰기 담당·재개 기록 |

두 fixture에서 각각 생성한 7개 OpenSpec과 실제 CLI 검사는 구현·도구 관측 근거
native 전체 작업 흐름·사용자 R2·Allsen 제품·운영 인수의 상태는 [기능 인수 기록](functional-acceptance.md)에서 별도 관리
H01–H26와 원문 선정 전체 대응은 [원문 요구 대조](requirements-coverage.md) 참조

## 기존 구성 정리

상위 workspace/AGENTS.md 재생성 제외, SecondBrain은 활성 대상에서 제외
Allsen Adapter 생성 계획 철회, 스킬 설치를 위한 제품 도구 전환 제외
runner의 deploy/runners 통합 방향은 독립 인프라 작업에서 소비자·복구 검증 후 진행

현재 설치 전환 상태는 [전환 안내](../skills-migration.md), 유지보수 방법은 [검사 안내](../maintenance.md) 참조
