# 기능 구현과 인수 기록

기준일: 2026-09-22
대상: 공통 스킬 22개, 각 fixture에 생성한 OpenSpec 7개, Web/API·Streaming 실행 예제
현재 상태: 통합 인수 OPEN — 최종 commit·통합 검사 수·실제 CI 결과는 통합 담당자 확정 대기

[원문 요구 대조](requirements-coverage.md)의 7+7+4 선정·공통 5기능·3분야·2예제·H01–H26를 유지하는 현재 구현과 관측 기록
아래 수치는 worker 실행 기록과 통합 담당자가 전달한 실제 관측값이며 최종 후보의 합산 통과 수로 사용 제외
최신 통합 Web·회귀 실행 시점은 working HEAD `481f6a8`과 통합 담당자의 미커밋 docs/core 변경이 포함된 상태로 기록
최종 candidate·CI 근거로 승격하기 전 commit과 영향 검사 확인 필요
소스 존재, 도구 실행, native 에이전트 전체 흐름, 사용자 설치 R2, Allsen 제품·운영 인수를 별도 판정

## 구현과 관측한 검사

각 행은 해당 검사에서 확인한 범위만 나타내는 중간 기록

| 대상 | 실제 구현·근거 위치 | 관측과 현재 판정 |
| --- | --- | --- |
| 공식 리뷰 후보 검사 | [candidate helper](../../skills/code-review/scripts/check-candidate.py), [회귀 검사](../../tests/test_review_candidate.py) | 10개 PASS; assume-unchanged·skip-worktree로 숨긴 변경의 실제 red→green 포함, 필수 spec·dirty·stale 후보 거부 |
| OpenSpec CLI 생명주기 | [고정 의존성](../../fixtures/openspec/package.json), [실제 CLI 검사](../../fixtures/openspec/test_lifecycle.py) | CLI 1.13.1의 5개 PASS, 22.53초; init·반복 init·update·canonical archive·invalid spec 거부·기존 문서 보존 |
| 새 세션의 격리 update | [초기 구성·갱신 절차](../../skills/development-tooling/references/openspec-setup.md)와 위 CLI 검사 | 기존 core profile·profile 미설정 두 경우 포함; 원래 사용자 설정 바이트 동일, 생성 스킬 7개 유지 |
| 두 fixture의 OpenSpec | [Web/API change](../../fixtures/web-api/openspec/changes/accept-web-api/proposal.md), [Streaming change](../../fixtures/streaming/openspec/changes/accept-streaming/proposal.md) | 각 fixture의 7개 생성과 실제 CLI strict validate PASS; 제품 기능 검증·완료 archive와 별개 |
| 선택 설치·native catalog | [project-workflow](../../skills/project-workflow/SKILL.md), 설치 위치의 필수 참고 자료 | 격리 선택 설치와 실제 native Codex catalog의 project-workflow 발견 관측; 전체 실행 인수는 대기 |
| native 읽기 전용 canary | 로컬 `.reports/native-result.txt`, `.reports/native-simple-read-result.txt` | canary 쓰기 DENIED 관측; shell 파일 읽기도 두 시도에서 policy DENIED, 실제 읽기 전용 리뷰 실행은 미인수 |
| 네 routing 사례 | [workflow](../../skills/project-workflow/SKILL.md), [follow-up](../../skills/project-workflow/references/followup-and-resumption.md) | 설치 지침의 독립 읽기 검토 완료; 실제 PR·concurrency lock·native 전체 실행 성공과 별개 |
| Web/Python worker | [실행 기록](../../fixtures/web-api/RUN-EVIDENCE.md), [사용법](../../fixtures/web-api/USAGE.md) | Python HTTP 12개·Edge Test 7개·JUnit 거부/집계 회귀 29개 PASS 관측; 아래 통합 관측과 구분 |
| Web/Python 통합 재실행 | 로컬 `fixtures/web-api/.reports/integrated-web-python/summary.json` | Python 12개·Edge 7개 PASS, failures/errors/skipped 0; 두 공통 JUnit 판정 PASS, 소유 process/listener 잔류 없음, source·locks 바이트 동일 |
| 통합 root 회귀 | [JUnit 검사](../../tests/test_python_reports.py), [candidate 검사](../../tests/test_review_candidate.py) | JUnit 29개 + candidate 10개 = 39개 PASS, 9.92초; 위 candidate 10개와 중복 합산 제외 |
| 실제 Playwright MCP | 위 worker 기록, [MCP 절차](../../skills/webapp-testing/references/playwright-evidence.md) | tools/list 25개 발견·실제 Edge DOM·browser_close 관측; 25개를 Test 통과 수에 합산 제외 |
| Streaming worker | [실행 fixture](../../fixtures/streaming/run.py), [회귀 검사](../../tests/test_streaming_probe.py), [사용법](../../fixtures/streaming/README.md) | 단위 13개·CPU 수신 12프레임·약 2초 outage·새 12프레임·Chromium WebRTC decoded 증가 26 관측 |
| Streaming 동시 실행·정리 | 위 fixture의 개별 포트·stream·보고서·소유 프로세스 관리 | 두 동시 실행과 cleanup 관측; epoch·cleanup·outage 결함 수정 중이므로 최종 인수 대기 |
| Windows CI fixture job | [check.yml의 usage-fixtures](../../.github/workflows/check.yml) | job 작성, 아직 push·실행 미관측; 실제 후보·run·artifact 연결 대기 |

candidate helper의 READY는 제품 검사 실행이나 리뷰 권한 확인을 뜻하지 않는 결과
CLI strict validate는 OpenSpec 문서 형식·요구 구조 검사이며 구현 동작 PASS와 별개
Streaming의 기존 관측은 수정 전 기록으로 보존하고 수정 후 최종 검사 수·새 보고서·후보를 추가할 때 재판정

## native 실행과 routing의 한계

중첩 native Codex에서 canary 파일 쓰기 거부는 관측한 권한 동작
같은 환경의 shell 파일 읽기 두 시도도 정책 거부되어 필요한 지침과 소스를 읽은 실제 리뷰 실행은 수용하지 않은 상태
거부된 파일 읽기 재시도나 정책 약화·강제 우회 없이 허용되는 입력 경로에서 다시 측정할 항목

검증된 committed snapshot을 stdin으로 제공하는 경로는 검토 가능한 다음 후보
실제 실행 전까지 읽기 전용 에이전트 리뷰를 영구 불가 또는 인수 완료로 단정하지 않는 기준
허용 경로의 실제 입력 수신·같은 후보·분리된 두 축 판단·쓰기 거부·트리 보존 관측 필요

설치 지침을 별도로 읽어 검토한 네 사례의 기대 행동

| 사례 | 독립 지침 검토의 결정 | 이 기록이 증명하지 않는 동작 |
| --- | --- | --- |
| 공식 인수에 필요한 OpenSpec spec 없음 | BLOCKED, Standards 진단으로 공식 인수 대체 불가 | 실제 native 도구 실행 |
| 같은 event/review ID·head가 처리 완료이고 finding 해결 | 현재 상태 확인 후 no-op | 실제 PR 쓰기 중복 방지·동시 실행 잠금 |
| handoff의 head와 실제 head 불일치 | 후보·입력 재평가, 무효화된 검사·리뷰 갱신 | 기록만 받은 다른 작업의 실제 재개 |
| 같은 제안의 구현 승인 존재, 모호함 없이 계속 요청 | 기존 승인 재사용 후 구현·검사 계속 | 전체 구현·검사·리뷰·전달의 성공 |

## 최종 통합 기록

통합 담당자가 동일 후보에서 확정할 항목
진행 중 검사의 존재나 이전 worker 통과 수만으로 빈 항목을 성공 처리하지 않는 기준

| 항목 | 현재 값 | 확정할 근거 |
| --- | --- | --- |
| base·최종 commit·공통 skill revision | PENDING | 통합 담당자가 고정한 실제 SHA와 명세 경로 |
| 최종 유지보수·candidate·parser 검사 | 최종 귀속 PENDING | working tree에서 39개 PASS 관측; 전체 유지보수 결과·최종 후보 연결은 통합 담당자 확정 |
| OpenSpec 실제 CLI 검사 | 관측 5 PASS, 22.53초 | 최종 후보에 유효한 보고서 귀속 확인 |
| 두 fixture strict validate | 실제 CLI PASS 관측 | 최종 명세 변경 시 영향 검증 |
| 통합 Web/API·브라우저 검사 | 관측 12 Python + 7 Edge PASS | 두 JUnit 판정·cleanup·바이트 보존 확인; 최종 후보 귀속 PENDING |
| 수정 후 Streaming·동시 실행·cleanup | PENDING | epoch·outage·descendant 정리 회귀와 실제 수신 보고서 |
| 같은 후보의 Spec·Standards 리뷰 | PENDING | finding별 처리·영향 검사·실제 native 실행 관측 |
| handoff·canonical spec·archive | PENDING | 두 fixture의 남은 tasks와 제품 전달 정책 |
| 실제 CI | NOT_RUN | push 후 repository·head·run·artifact URL 대조 |

두 fixture의 진행 위치는 [Web/API tasks](../../fixtures/web-api/openspec/changes/accept-web-api/tasks.md)와 [Streaming tasks](../../fixtures/streaming/openspec/changes/accept-streaming/tasks.md)에서 관리
이 문서는 task 목록·runtime·공통 상태 저장소를 추가하는 대신 관측과 미완료 범위를 설명하는 기록

## 후속 인수 게이트

- 사용자 설치 R2: 기존 설치·수정 백업, 선택 전환·복구, 같은 이름의 공급 하나, 실제 Desktop 발견·호출과 두 예제 재실행
- Allsen 제품: 기존 Taskfile·CI·명세로 실제 변경·검사·독립 리뷰·인계, 제품 RTSP→추론→WebRTC 전달과 source/frame 상관 확인
- GPU·tracker: 실제 요구 GPU에서 모델·출력 검증, 정한 단절 정책에 따른 객체 ID 연속성 또는 재설정 확인; 현재 CPU fixture로 대체 불가
- PR·CI: 실제 이벤트 중복 처리·동시 쓰기 제어와 required checks·후보·run·artifact 연결 확인
- 운영: infra 소유의 일회성 runner 종료·crash 복구, deploy 소유의 승인·대상 거부·건강 실패·복구 기록

필수 자원 부재는 BLOCKED, 실행하지 않은 검사는 NOT_RUN, 실패한 검사는 FAIL로 유지
공통 스킬 수·선택 설치·CLI 생성·fixture 부분 성공을 사용자 R2·제품·운영 전체 인수로 합산하지 않는 기준
