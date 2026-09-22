# 원문 요구와 현재 구현 범위

기준일: 2026-09-22
검사한 구현: `dee18d7131394858172adb067d28dccb972f5ee2`
근거: 사용자 첨부 구축 지시문 「0. 수행할 작업」의 5·6·16·17·18절과 해당 commit의 추적 파일

**현재 19개는 범용 스킬의 공급 목록이며 원문 전체 기능의 완성 목록이 아님**

npx skills로 설치 방식을 단순화하라는 요청을 기능 범위 축소로 처리한 판단 정정
전체 기능을 담기 전에 설치 전환을 다음 단계로 잡은 순서도 정정
19개를 최종 개수로 고정하거나 9개 이름의 통합을 기능 보존 완료로 집계하는 기준 철회

## 19개의 실제 구성

- 기존 범용 스킬 13개
- Matt 계열 독립 스킬 4개: domain-modeling·grilling·codebase-design·code-review
- Superpowers 계열 독립 스킬 2개: test-driven-development·verification-before-completion

원문의 OpenSpec 7개·Matt 7개·Superpowers 4개에는 의도적으로 서로 다른 공급 위치와 통합 가능한 절차 포함
여기에 공통 작업 연결 기능 5개와 Web·Python·Streaming 기능, 두 실행 예제 요구까지 포함
기존 13개와 숫자만 합산하여 최종 스킬 수를 정하는 방식 제외

아래의 보존은 파일·내용의 존재 의미이며 실제 Codex 호출이나 원문 시나리오 인수 통과와 별개

## 선정 스킬별 대조

| 원문 선정 | 현재 위치·처리 | 남은 일 |
| --- | --- | --- |
| openspec-explore | 공통 19개에 미포함; 제품에서 생성할 스킬 | 실제 제품의 생성·발견·조사 흐름 연결 |
| openspec-propose | 동일 | 기존 문서와 제안·명세·설계·작업 연결 |
| openspec-apply-change | 동일 | 승인된 변경의 구현 흐름 연결 |
| openspec-update-change | 동일 | 진행 중 변경 사항의 명세·작업 갱신 검증 |
| openspec-verify-change | 동일 | verify를 명시한 생성 설정과 실제 명세 대조 검증 |
| openspec-sync-specs | 동일 | 승인된 변경의 정본 반영 검증 |
| openspec-archive-change | 동일 | 완료 변경 보관까지 실제 한 흐름으로 실행 |
| setup-matt-pocock-skills | 독립 공급 종료; development-tooling으로 일부 책임 이동 | tracker·문서·기존 CLAUDE 보존·AGENTS 진입·실제 발견까지 대체 절차 검증 |
| domain-modeling | skills/domain-modeling에 보존 | 실제 제품 문서의 용어·모델·ADR 반영 검증 |
| grill-with-docs | grilling/references/record-decisions.md로 일부 통합 | 협의 조건·domain-modeling 연결·결정 기록까지 누락 대조 |
| grilling | skills/grilling에 보존 | 명시된 협의에서 호출하고 승인된 구현마다 재질문하지 않는 동작 검증 |
| codebase-design | skills/codebase-design에 보존 | 제품 규칙 우선 적용과 실제 설계 검토 |
| code-review | skills/code-review에 보존 | 같은 후보·명세·검사 근거로 독립 두 축 검토, 누락·dirty 후보 실패 검증 |
| writing-for-agents | markdown-authoring/references/writing-for-agents.md로 통합 | 실제 에이전트 문서 작성 요청의 발견·실행·필수 지침과 참고 자료 구분 검증 |
| test-driven-development | skills/test-driven-development에 보존 | 실제 실패→구현→재검증 시나리오 |
| systematic-debugging | 기존 skills/systematic-debugging 단일 공급 유지 | 실제 재현·원인·수정 검증 |
| verification-before-completion | skills/verification-before-completion에 보존 | 오래된 결과·0 tests·검사 누락을 완료로 보고하지 않는 사례 |
| receiving-code-review | code-review/references/receiving-review.md로 통합 | 리뷰 요청 없이 피드백만 받은 경우도 절차에 진입하는지 검증 |

이전 OpenSpec 시험 폴더의 7개 생성 확인은 실제 제품에서 전체 흐름이 연결됐다는 근거로 사용 제외
공통 저장소에 OpenSpec 복사본을 추가하여 이중 공급하는 방식도 제외
기존 이름을 합칠 때에는 호출 조건·필수 내용·참조·실행 결과의 동등성 확인 필요

## 공통 작업 연결 기능 5개

원문 6절의 이름을 없애더라도 아래 기능과 완료 기준은 유지
현재 소유 스킬에 일부 절차를 옮긴 상태이며 전체 흐름의 동등성 미검증

| 기능 | 현재 처리 | 보완·검증 결과물 |
| --- | --- | --- |
| 시작·초기 구성 | development-tooling에 일부 이동 | 실제 문서·OpenSpec·환경·명령과 Codex 발견 확인 |
| 작업 진행 | OpenSpec·구현 스킬·완료 판단으로 분산 | change 선택→승인 확인→구현→검사→리뷰, 기준별 증거·차단 목록 |
| 공식 리뷰 | code-review에 일부 통합 | 고정 후보의 Spec·Standards 독립 결과와 지적별 처리 상태 |
| PR 후속 작업 | github-operations 참고 자료 | 지정 PR·head·처리 이벤트·단일 쓰기 담당·다음 조건, 중복 처리 시험 |
| 인계·재개 | github-operations 참고 자료 | 전체 대화 없이 다른 작업이 위치·후보·근거·미완료를 찾아 재개 |

문서의 소유자 표만으로 작업 연결 완료 처리 금지
기존 스킬의 자연스러운 진입 조건으로 연결되지 않는 기능은 실제 시나리오를 근거로 보완
스킬 이름 유지 여부는 기능 보존을 확인한 뒤 결정

## 분야별 기능과 실행 예제

| 원문 요구 | 현재 상태 | 구현·인수 범위 |
| --- | --- | --- |
| Web | webapp-testing 등 일반 지침 존재; 원문 조합의 연결 미완료 | Playwright MCP 탐색·재현과 저장된 Playwright Test 구분, 실제 URL·계정 fixture·정상·오류·권한·입력 실패 검사 |
| Python | 개발 도구 지침 존재; 제품 검사·결과 parser 연결 미완료 | uv·기존 Python 명령, 실제 케이스 수·실패·보고서 parser와 0 tests·누락·허위 성공 거부 |
| Streaming | 요구된 실행 fixture 미구현 | MediaMTX·FFmpeg 합성 RTSP 발행·읽기·중단·재개, 실제 새 프레임과 WebRTC 수신 검사 |
| Web/API 실행 예제 | 미완료 | 작은 HTTP 동작과 Playwright 시나리오를 명세부터 검사·리뷰·인계까지 실제 실행 |
| Streaming 실행 예제 | 미완료 | 같은 공통 revision으로 합성 소스 단절·복구 검증, 가능한 브라우저 수신까지 실행 |

분야별 기능은 해당 스킬의 references·구체적인 scripts와 재실행 가능한 예제에 배치
별도 팩 설치 계층 제거를 세 분야 기능의 제거로 해석하는 기준 철회
실제 코드 배치는 구현 전 기존 스킬·제품 도구와 대조하고 중복 없는 소유자 선택

MediaMTX는 시험용 미디어 소스로 사용하고 기존 제품 미디어 서버 교체 제외
합성 소스 시험과 실제 제품 RTSP→추론→WebRTC 검증을 별도 기록
CPU mock·새 프레임 수신·GPU 추론·tracker ID 유지의 결과를 서로 대체하지 않는 기준
필수 브라우저·GPU 환경 부재는 해당 검사 BLOCKED로 기록하고 통과 집계 제외

## 완료 보고 정정

R1 테스트 33개·하위 사례 12개는 tests/test_packages.py의 패키지 무결성·출처·참조·실패 입력 검사
두 스킬의 시험 설치는 설치 파일 확인이며 두 실행 예제의 기능 검증 미실행
R1의 독립 검토는 당시 축소된 정리 계획을 대상으로 한 결과이며 원문 전체 범위 충족의 근거로 사용 제외

원문의 H01–H26 중 권한·병렬 자원·인계·PR 중복 처리·실제 CI·runner·배포 요구도 별도 유지
지침 존재와 실제 권한·CI 강제·운영 실패 시험을 각각 구분
공개 push·패키지 검사 성공을 제품 기능이나 운영 인수 성공으로 확대 해석하는 기준 철회

## 수정한 진행 순서

1. 원문 기능별 현재 파일·공급 경로·누락·인수 조건 대조 — 이 문서로 정정
2. OpenSpec 7개와 공통 작업 흐름 연결, 통합한 9개 이름의 기능 보존 재검증 — 미완료
3. Web·Python·Streaming 지침·필요한 도구·두 실행 예제 구현 및 실패 사례 검증 — 미완료
4. 해당 기능의 실제 Codex 호출과 동일 revision 재사용 검증 — 미완료
5. 대체 기능이 검증된 사용자 설치본만 백업·전환 — 미완료
6. Allsen 실제 작업·CI와 별도 운영 저장소의 runner·배포·복구 인수 — 미완료

최종 스킬 이름·개수는 기능을 빠짐없이 배치한 결과로 결정
이번 정정은 문서와 완료 판정의 수정이며 빠진 기능 구현의 완료 기록이 아님
현재 사용자 설치본·플러그인 설정의 선제 비활성화 제외
