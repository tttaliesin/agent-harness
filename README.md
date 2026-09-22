# Agent Harness

Codex에서 필요한 개발 지침을 골라 쓰는 공통 스킬 모음
설계·디버깅·리뷰·Git·문서 작업의 지침과 필요한 보조 자료를 `npx skills`로 설치
실제 작업은 Codex와 제품의 기존 빌드·검사 명령으로 수행

현재 통합 소스는 공통 스킬 22개와 Web/API·Streaming 실행 예제 두 개로 구성
기존 19개에 project-workflow·python-testing·streaming-testing 추가, OpenSpec 7개는 고정 CLI가 각 fixture와 제품에 생성
구현·관측한 fixture 검사·실제 Codex 전체 흐름·사용자 설치 전환의 상태는 [기능 인수 기록](docs/implementation/functional-acceptance.md)에서 구분
전체 요구와 남은 제품·운영 범위는 [원문 요구 대조](docs/implementation/requirements-coverage.md) 참조

## 첫 사용

Node.js·npx와 GitHub 접근 가능한 환경 필요
다음은 PowerShell·일반 shell에서 사용할 수 있는 개인 설치 예시

```sh
npx skills add tttaliesin/agent-harness --list
npx skills add tttaliesin/agent-harness --skill readme-authoring --agent codex --global
npx skills list --agent codex --global
```

Codex에서 `$readme-authoring README를 처음 쓰는 사람이 따라갈 수 있게 정리해줘` 요청
수정된 README에서 첫 작업의 전제·명령·결과 확인 경로를 찾고 실제 실행한 검사와 미검증 범위 확인
설치 목록에 이름이 나타나는지 확인한 뒤 실제 작업에서 해당 지침이 사용되는지 확인
스킬이 보이지 않으면 Codex의 스킬 목록을 다시 확인하고 필요 시 앱 재시작

프로젝트 범위 설치가 필요하면 해당 저장소에서 `--global`을 생략하고 사용자 범위의 같은 이름과 중복 여부 확인
각 스킬은 이름으로 선택 설치하며, 아래 전체 목록을 한 번에 설치할 필요 없음
설치 옵션과 지원 범위는 [Skills CLI](https://github.com/vercel-labs/skills), 로딩 위치는 [Codex 스킬 문서](https://developers.openai.com/codex/skills) 참조

## 작업에 맞는 스킬 선택

| 작업 | 선택할 스킬 | 대표 결과 |
| --- | --- | --- |
| 승인된 변경의 진행·재개 | [project-workflow](skills/project-workflow/SKILL.md) | 기존 승인과 OpenSpec change를 회수하고 구현·제품 검사·리뷰·인계 연결 |
| 실패 원인 조사·검증 | [systematic-debugging](skills/systematic-debugging/SKILL.md), [webapp-testing](skills/webapp-testing/SKILL.md) | 재현·원인 근거·실제 검사 결과 |
| Python·영상 수신 검사 | [python-testing](skills/python-testing/SKILL.md), [streaming-testing](skills/streaming-testing/SKILL.md) | 실제 JUnit case 판정, RTSP 단절·새 프레임 복구·WebRTC 수신 근거 |
| 구현·완료 확인 | [test-driven-development](skills/test-driven-development/SKILL.md), [verification-before-completion](skills/verification-before-completion/SKILL.md) | 의미 있는 테스트와 근거에 맞는 완료 보고 |
| 설계·요구 정리 | [domain-modeling](skills/domain-modeling/SKILL.md), [grilling](skills/grilling/SKILL.md), [codebase-design](skills/codebase-design/SKILL.md), [api-design-principles](skills/api-design-principles/SKILL.md) | 용어·결정·모듈 경계·인터페이스 정리 |
| 변경 검토 | [code-review](skills/code-review/SKILL.md), [differential-review](skills/differential-review/SKILL.md) | 명세·코드 검토 또는 보안 중심 변경 분석 |
| Git·병렬 작업 | [github-operations](skills/github-operations/SKILL.md), [multi-github-account-operate](skills/multi-github-account-operate/SKILL.md), [parallel-worktree-development](skills/parallel-worktree-development/SKILL.md) | 승인된 전달·계정 선택·작업 분담 |
| 문서·구성도 | [markdown-authoring](skills/markdown-authoring/SKILL.md), [readme-authoring](skills/readme-authoring/SKILL.md), [design-doc-mermaid](skills/design-doc-mermaid/SKILL.md) | 읽고 사용할 수 있는 문서·도식 |
| 소유권·개발 환경·CI | [workspace-governance](skills/workspace-governance/SKILL.md), [development-tooling](skills/development-tooling/SKILL.md), [github-actions-workflows](skills/github-actions-workflows/SKILL.md) | 기존 프로젝트 책임에 맞는 정책·도구·workflow |

예: 테스트 실패 요청에 디버깅 스킬을 사용하고, 원인을 고친 뒤 제품의 기존 Taskfile·npm·Go·Python 명령으로 확인
제품별 명세·검사 명령은 해당 저장소가 소유하며 별도 Adapter 설정 없이 사용
스킬 지침과 실제 CI·권한 강제는 서로 다른 근거로 확인

## 구현을 따라가 볼 실행 예제

아래 두 예제는 제품의 기존 명령과 공통 스킬을 연결하는 재실행 경로
준비 도구·실행 위치·보고서 확인은 각 사용법에서 확인

| 예제 | 입력과 확인할 동작 | 사용법·요구 |
| --- | --- | --- |
| Web/API | 이름 입력의 인사 응답, 잘못된 입력·권한·서버 오류와 화면 복구 | [Web/API 실행 안내](fixtures/web-api/USAGE.md), [Web/API 요구](fixtures/web-api/openspec/changes/accept-web-api/specs/web-api/spec.md) |
| Streaming | 합성 RTSP 소스의 발행·중단·재개와 실제 디코딩·브라우저 WebRTC 수신 | [Streaming 실행 안내](fixtures/streaming/README.md), [Streaming 요구](fixtures/streaming/openspec/changes/accept-streaming/specs/streaming/spec.md) |

예: project-workflow가 설치된 작업에서 `$project-workflow 승인한 change의 남은 구현과 검사를 계속하고 미완료 인수 조건을 기록해줘` 요청
예상 결과는 change의 기존 승인 재사용, 실제 제품 명령 실행, 후보에 연결한 검사·리뷰·다음 행동 기록
현재 선택 설치와 native Codex catalog의 project-workflow 발견은 관측했으며 실제 전체 흐름 인수는 진행 중
CPU 영상 수신 결과와 GPU 추론·tracker ID·Allsen 제품 전달·운영 결과는 [인수 기록](docs/implementation/functional-acceptance.md)에서 별도 판정

## 갱신과 기존 설치

설치본을 직접 수정했다면 갱신 전에 원본과 비교하고 변경을 보존

```sh
npx skills update readme-authoring --global
```

기존 workflow-core·matt-engineering·superpowers-execution 설치 사용자는 [전환 안내](docs/skills-migration.md)에서 중복 공급과 로컬 수정 확인
저장소 변경만으로 사용자 설치본·플러그인 설정이 자동 전환되지는 않는 구조

## 유지보수와 출처

- [저장소 검사·upstream 갱신](docs/maintenance.md)
- [공통 정책과 제품의 책임](docs/implementation/layout-map.md)
- [스킬 관리](docs/codex-skill.md)
- [서드파티 출처·라이선스](THIRD_PARTY_NOTICES.md)

Python·uv·just는 이 저장소의 유지보수 검사용 도구
스킬 설치 자체에는 필요하지 않으며 개별 보조 도구의 요구 사항은 해당 스킬에서 안내
