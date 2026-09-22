# 원문 요구와 현재 구현 범위

기준일: 2026-09-22
기준 요구: 사용자 첨부 구축 지시문 「0. 수행할 작업」의 5·6·16·17·18절과 기존 H01–H26 목적
현재 통합 소스의 구현 위치와 남은 인수 조건 대조
최종 후보 commit·통합 검사 수·실제 CI run은 [기능 인수 기록](functional-acceptance.md)에 통합 담당자가 확정할 항목

## 현재 공급과 요구 범위

공통 스킬 22개: 기존 범용 13개, Matt 독립 4개, Superpowers 독립 2개에 project-workflow·python-testing·streaming-testing 추가
OpenSpec 7개는 공통 22개와 별도로 CLI 1.13.1이 Web/API·Streaming 각 fixture의 `.agents/skills/`에 생성
22와 7은 공급 위치의 개수이며 기능 인수 통과 수와 별개

원문 OpenSpec 7개·Matt 7개·Superpowers 4개, 공통 작업 연결 5개, Web·Python·Streaming 3분야, 실행 예제 2개와 H01–H26 범위 유지
설치 방식 단순화와 이름 통합을 요구 축소나 기능 보존 완료로 취급했던 판단 정정
이전 19개 공급 단계와 R1의 패키지 검사·시험 설치는 역사적 부분 근거로 보존

## 선정 스킬별 대조

원문 선정 이름과 현재 소유 위치의 대응
생성·구현·검사 결과는 [기능 인수 기록](functional-acceptance.md)에서 구분하고 실제 제품 사용은 별도 확인

| 원문 선정 | 현재 위치·처리 | 남은 인수 범위 |
| --- | --- | --- |
| openspec-explore | CLI 생성; [7개 선택 절차](../../skills/project-workflow/references/workflow-routing.md) | 실제 change 조사와 요구 회수 |
| openspec-propose | CLI 생성; 두 fixture의 proposal·design·specs·tasks 존재 | native 요청에서 제안·승인 연결 |
| openspec-apply-change | CLI 생성; [project-workflow](../../skills/project-workflow/SKILL.md)에서 호출 | 승인된 구현과 제품 검사 전체 실행 |
| openspec-update-change | CLI 생성; 같은 change의 요구 변경 경로 | 실제 요구 변경 후 영향 검사 |
| openspec-verify-change | CLI custom profile에 명시하여 각 fixture에 생성 | 실제 후보의 요구·시나리오 대조 |
| openspec-sync-specs | CLI 생성; canonical spec 반영을 lifecycle 검사로 확인 | 두 fixture 정본 반영·strict validate 완료; 실제 제품 인수는 별도 |
| openspec-archive-change | CLI 생성; 실제 CLI archive와 canonical spec 검사 | 두 fixture 보관 완료; 실제 제품 전달·보관은 별도 |
| setup-matt-pocock-skills | [development-tooling 초기 구성](../../skills/development-tooling/references/openspec-setup.md)으로 통합 | tracker·기존 문서·승인 회수와 실제 제품 진입 |
| domain-modeling | [domain-modeling](../../skills/domain-modeling/SKILL.md) 유지 | 제품 용어·모델·ADR 적용 |
| grill-with-docs | [grilling 결정 기록](../../skills/grilling/references/record-decisions.md)으로 통합 | 필요한 협의와 domain-modeling 연결 |
| grilling | [grilling](../../skills/grilling/SKILL.md) 유지 | 승인된 구현의 반복 질문 없이 필요한 결정만 협의 |
| codebase-design | [codebase-design](../../skills/codebase-design/SKILL.md) 유지 | 제품 규칙에 맞춘 실제 설계 검토 |
| code-review | [후보 검사·Spec/Standards](../../skills/code-review/SKILL.md) 구현 | 분리된 native stdin 리뷰 완료; 제품 권한 경계·자동 호출은 별도 |
| writing-for-agents | [markdown-authoring 참고 자료](../../skills/markdown-authoring/references/writing-for-agents.md)로 통합 | 문서 요청에서 발견·필수 지침 적용 |
| test-driven-development | [test-driven-development](../../skills/test-driven-development/SKILL.md) 유지 | 실제 제품의 실패→구현→재검증 |
| systematic-debugging | [기존 단일 공급](../../skills/systematic-debugging/SKILL.md) 유지 | 실제 재현·원인·수정 검증 |
| verification-before-completion | [verification-before-completion](../../skills/verification-before-completion/SKILL.md) 유지 | 현재 후보·실제 결과·미완료의 정확한 판정 |
| receiving-code-review | [code-review 피드백 검증](../../skills/code-review/references/receiving-review.md)으로 통합 | 피드백에서 진입해 근거에 맞춘 수정·재검사 |

OpenSpec의 실제 init·반복 init·격리 update·canonical archive·잘못된 spec 거부·기존 문서 보존은 [CLI lifecycle 검사](../../fixtures/openspec/test_lifecycle.py) 5개 통과로 관측
기존 core profile 또는 profile 미설정 상태에서도 별도 XDG 경로의 후속 update가 원래 사용자 설정 바이트와 7개 생성 스킬을 보존하는 경우 포함
CLI의 파일 생명주기 검사를 native Codex의 전체 구현·리뷰·인계 실행 인수로 확대하지 않는 기준

## 공통 작업 연결 기능 5개

원문 6절의 기능과 완료 기준 유지
현재 진입점과 구체적인 구현을 연결하되 지침의 존재를 운영 강제로 대체하지 않는 판정

| 기능 | 구현 진입점 | 관측과 남은 조건 |
| --- | --- | --- |
| 시작·초기 구성 | [development-tooling](../../skills/development-tooling/SKILL.md), [OpenSpec setup](../../skills/development-tooling/references/openspec-setup.md) | 기존 tracker·CLAUDE·AGENTS·승인 보존 절차, CLI 검사 관측; 실제 제품 진입 인수 남음 |
| 작업 진행 | [project-workflow](../../skills/project-workflow/SKILL.md) | 선택 설치·native catalog 발견과 승인 재사용 지침 검토 관측; 전체 실행 인수 남음 |
| 공식 리뷰 | [code-review](../../skills/code-review/SKILL.md), [candidate helper](../../skills/code-review/scripts/check-candidate.py) | helper 10개 통과, 숨긴 Git index flags 차단; 분리된 native stdin 리뷰·쓰기 거부·tree 보존 관측; Desktop 제품 실행은 별도 |
| PR 후속 작업 | [github-operations 후속 절차](../../skills/github-operations/references/followup-and-handoff.md) | 같은 이벤트·head의 no-op 지침 독립 검토; 실제 PR 중복 쓰기·동시성 시험 남음 |
| 인계·재개 | [project-workflow 재개 절차](../../skills/project-workflow/references/followup-and-resumption.md) | stale head의 재평가 지침 독립 검토; 기록만 받은 다른 작업의 실제 재개 남음 |

필수 spec 부재의 BLOCKED, 처리한 event/review ID와 같은 head의 no-op, 오래된 handoff head의 재평가, 기존 구현 승인 재사용의 네 사례는 설치 지침을 읽은 독립 routing 검토
실제 PR 처리·동시 실행 잠금·읽기 전용 에이전트 실행 성공의 근거로 사용 제외

## 분야별 기능과 실행 예제

현재 구체적 구현과 원문 인수 범위의 대응

| 원문 요구 | 구현·실행 진입점 | 관측과 남은 범위 |
| --- | --- | --- |
| Web | [webapp-testing](../../skills/webapp-testing/SKILL.md), [MCP와 Test 구분](../../skills/webapp-testing/references/playwright-evidence.md) | 통합 Edge 7개·JUnit 판정·cleanup 관측, 실제 MCP DOM은 worker 근거; 고정 후보 및 실제 CI 귀속 확인 |
| Python | [python-testing](../../skills/python-testing/SKILL.md), [JUnit 검사기](../../skills/python-testing/scripts/check-junit.py) | 통합 HTTP 12개·JUnit 회귀 29개 관측; 0 cases·누락·허위 성공 거부 |
| Streaming | [streaming-testing](../../skills/streaming-testing/SKILL.md), [decoded-frame probe](../../skills/streaming-testing/scripts/stream_probe.py) | CPU RTSP·WebRTC 관측; epoch·cleanup·outage 수정 후 실제 고정 후보 검사 통과; 상세 결과는 기능 인수 기록 |
| Web/API 실행 예제 | [Web/API 사용법](../../fixtures/web-api/USAGE.md), [Web/API 요구](../../fixtures/web-api/openspec/specs/web-api/spec.md), [Web/API tasks](../../fixtures/web-api/openspec/changes/archive/2026-09-22-accept-web-api/tasks.md) | 정상·오류·권한·입력 시나리오 구현, 실제 CLI strict validate 통과; 고정 후보 검사·CI·리뷰 기록 연결, 제품 전체 흐름은 별도 |
| Streaming 실행 예제 | [Streaming 사용법](../../fixtures/streaming/README.md), [Streaming 요구](../../fixtures/streaming/openspec/specs/streaming/spec.md), [Streaming tasks](../../fixtures/streaming/openspec/changes/archive/2026-09-22-accept-streaming/tasks.md) | 발행·중단·새 프레임·브라우저 수신 구현, 실제 CLI strict validate 통과; 수정 후 고정 후보와 실제 CI 통과, 제품 전체 흐름은 별도 |

MediaMTX는 시험용 합성 소스이며 기존 제품 미디어 서버 교체 대상에서 제외
합성 CPU transport·실제 제품 RTSP→추론→WebRTC 전달·GPU 추론·tracker ID 유지는 각각 별도 요구와 결과
필수 브라우저·GPU 부재는 해당 검사 BLOCKED, 실행하지 않은 항목은 NOT_RUN으로 보존
재연결된 새 브라우저의 수신을 기존 브라우저 세션의 자동 복구나 tracker 연속성으로 대체하지 않는 기준

## H01–H26의 유지 범위

기존 요구 대조의 ID와 원문 목적 유지
아래는 책임·근거·남은 게이트의 대응이며 전체 통과표가 아님
공급 방식 전환으로 종료한 binding·hook·공통 registry의 원문 시험을 자동 PASS로 집계하지 않는 기준

| ID | 원문 목적 | 현재 근거와 남은 조건 |
| --- | --- | --- |
| H01 | 출처·SHA·license·포함 파일 증명 | 고정 출처·SHA·license·필수 참조 검사가 실제 Linux CI에서 통과 |
| H02 | 실제 Desktop 발견·호출·hook | 선택 설치·native catalog 발견 관측; 실제 호출 흐름·사용자 Desktop R2 남음, 자체 hook 공급 종료 |
| H03 | 반복 binding의 동일 결과 | binding 대신 선택 재설치·갱신 비교; OpenSpec 반복 init/update 관측과 사용자 R2 구분 |
| H04 | 사용자 수정 보존 | CLI 검사에서 기존 CLAUDE·AGENTS·사용자 설정 보존 관측; 사용자 설치 diff·백업·복구 남음 |
| H05 | 같은 이름 중복 탐지 | 공통 22개·fixture별 생성 7개 공급 분리; 실제 사용자 설치 중복 점검은 R2 |
| H06 | 필수 참조 누락 거부 | 필수 참조 실패 사례와 최종 패키지 검사 통과; 제품 필수 명세 거부 10개 검사에 포함 |
| H07 | 두 fixture에서 공통 재사용 | 같은 기능 후보의 Web/API와 Streaming 실행·분리된 native 리뷰·handoff 보완; 사용자 Desktop 자동 호출은 R2 |
| H08 | 필수 검사 약화 방지 | 필수 검사·누락 판정 지침 유지; 실제 CI required checks와 서버 강제 미검증 |
| H09 | 0 tests·보고서 누락 거부 | 실제 case·누락 검사와 29개 parser 회귀, 실제 CI XML 대조 완료 |
| H10 | exit 0·허위 PASS 불신 | 가짜 PASS·실패 XML 거부와 실제 candidate CI artifact 대조; 일반적인 보고서 위조의 독립 인증은 범위 밖 |
| H11 | timeout·도구 부재·자식 프로세스 정리 | 33개 미디어 회귀와 실제 고정 후보 실행 통과; timeout·도구 부재·고아 자식·빠른 404 검증 |
| H12 | 필수 GPU·브라우저 부재 구분 | BLOCKED·NOT_RUN 구분 유지; 실제 GPU·제품 환경 인수 남음 |
| H13 | 후보·명세·정책 변경 시 결과 무효화 | 고정 후보 helper·입력 hash·CI source candidate 귀속 확인; 실제 제품 정책 변경 전체 시험은 별도 |
| H14 | 변경 중인 후보·필수 명세 누락 구분 | helper 10개 통과에 dirty·missing spec·hidden index flags 거부 포함 |
| H15 | Spec·Standards 독립 판정 | 같은 기능 후보를 별도 native 읽기 전용 실행 두 개로 검토; 근거·인계 위치 지적 보완, 실제 제품 인수는 별도 |
| H16 | 리뷰의 실제 읽기 전용 경계 | read-only canary 쓰기 거부·stdin 소스 리뷰 두 실행·전후 tree 보존 확인; shell 읽기 거부와 Desktop 자동 호출 한계 명시 |
| H17 | 병렬 작업의 포트·데이터·로그 격리 | worker의 실제 동시 수신 두 개와 통합본의 자원 분리 회귀; 실제 제품 자원 시험은 별도 |
| H18 | 한 작업 정리 시 다른 작업 보존 | 통합본의 다른 작업 보존·부모 종료 후 자식 정리 회귀와 실제 cleanup PASS·잔류 없음 확인 |
| H19 | hook 재진입·중단 시 무한 실행 방지 | 자체 hook 공급 종료, 잔여 등록은 R2 확인; 원문 hook 시험 PASS 아님 |
| H20 | 전체 대화 없이 재개 | 독립 native 검토가 기록에서 저장소·후보·근거·다음 동작 식별, 부족했던 최신 결과·경로 보완; 실제 제품 재개는 별도 |
| H21 | 중복 PR 이벤트의 중복 쓰기 방지 | event/head 재조회·단일 쓰기 담당 지침 검토; 실제 중복 이벤트·동시 실행 차단 미입증 |
| H22 | 실제 CI 후보·run·artifact 연결 | 실제 Linux·Windows CI 두 job SUCCESS, 정확한 head·117/5/12/7 XML case·미디어 JSON artifact 대조 |
| H23 | 일회성 runner 제거·crash 복구 | infra 소유의 실제 runner 운영 시험 미완료 |
| H24 | 승인 없는 배포·잘못된 대상 거부 | deploy 소유의 승인·대상 실패 시험 미완료 |
| H25 | 배포·건강 실패·복구 기록 | deploy 시험 환경의 실패·복구 인수 미완료 |
| H26 | upstream 변경의 회귀 검증 | 출처·license·적용 patch·두 실행 예제 회귀 확인; 사용자 설치 갱신·복구 R2는 남음 |

## 완료 보고 정정

R1의 33개 테스트·하위 사례 12개는 당시 패키지 무결성·출처·참조·실패 입력 검사
당시 두 스킬 시험 설치와 축소된 정리 계획의 검토를 원문 전체 기능 완료로 설명한 판단 철회
이후 추가한 구현과 실제 fixture 관측을 반영하되 과거 기록을 현재 후보의 검증으로 재사용하는 방식 제외

## 완료한 공통 검증과 남은 인수

공통 스킬·두 예제의 구현, 실제 로컬·CI 검사와 native 리뷰 근거는 [기능 인수 기록](functional-acceptance.md)에 연결

1. 사용자 설치 R2에서 수정 백업·선택 전환·복구·실제 Desktop 발견·자동 호출 확인
2. Allsen 제품 작업·GPU·tracker·실제 제품 CI를 기존 명령·명세로 인수
3. 실제 PR 중복 이벤트·경합과 infra runner·배포·복구를 각 소유 범위에서 인수

현재 사용자 설치본·플러그인 설정의 선제 비활성화와 새 공통 runtime·adapter 계층 추가 제외
