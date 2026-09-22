# 기능 구현과 인수 기록

기준일: 2026-09-22
구현 범위: 공통 스킬 22개·제품별 OpenSpec 생성 7개·Web/API와 Streaming 실행 예제
원문 전체의 사용자 설치·Allsen·GPU·tracker·운영 인수는 아래 별도 게이트로 유지

## 확인한 후보와 결과

기능 후보: `768f5e8cefa686e1593b7284bfa9a6233221cb3a`
CI 준비 수정: `d06fb7929b77837d159b2178188930a3ad5e3c65` — 결과 폴더 생성과 artifact hash만 변경, 기능 소스 동일
후속 명세 보관·기록 정리는 기능 코드 변경과 구분하고 해당 커밋의 CI에서 다시 확인

| 검사 | 실제 결과 | 근거 |
| --- | --- | --- |
| 출처·license·필수 참조·무결성 | 공통 22개와 fixture 포함 PASS | `scripts/check-packages.py`, root lock, Linux CI |
| Linux 유지보수·실패 사례 | JUnit 실제 case 117개, failures/errors/skipped 0 | [후보 CI](https://github.com/tttaliesin/agent-harness/actions/runs/35724708653)의 package-and-helper-tests artifact; 하위 사례 포함 수치 |
| Python 보고서 parser | 29개 PASS | `tests/test_python_reports.py`; 누락·0 cases·가짜 PASS·stale·실패 XML·DTD 등 거부 |
| 리뷰 후보 | 10개 PASS | `tests/test_review_candidate.py`; dirty·필수 spec 누락·stale SHA·숨긴 Git index 변경 거부 |
| OpenSpec CLI 1.13.1 | 5개 PASS | `fixtures/openspec/test_lifecycle.py`; 7개 생성·반복·별도 갱신·보관·잘못된 명세 거부·사용자 설정과 문서 보존 |
| Web/API | HTTP 12개, 실제 Edge 7개 PASS | 기능 후보에서 재실행, 두 JUnit 판정 PASS, 소유 프로세스·listener 0개, 소스 28개 hash 보존 |
| Streaming 회귀 | 33개 PASS | `tests/test_streaming_probe.py`; 미관측 과거 epoch·빠른 404·부모 종료 후 자식·실행 권한 거부 포함 |
| Streaming 실제 수신 | 초기 12프레임, outage 2.0초·0프레임, 복구 12프레임·blue 표식·2.5초 | 기능 후보의 `fixtures/streaming/.reports/run-5fa417a9646c462ba452f7d709241e20/result.json` |
| WebRTC·정리 | 실제 browser decoded +27, cleanup PASS·survivors 0 | 같은 실행의 WebRTC 통계·화면 변화·Windows Job Object 결과 |
| 선택 설치 | Skills CLI로 22개 설치, 158개 파일 바이트 일치 | 격리 경로에서 검사; 설치된 후보·JUnit·미디어 helper 독립 실행 확인 |
| Playwright MCP | 실제 Edge DOM·browser_close, tools/list 25개 발견 | [worker 실행 기록](../../fixtures/web-api/RUN-EVIDENCE.md); Test 통과 수에 합산 제외 |

표의 회귀 검사 수는 Linux artifact의 일부이므로 서로 더해 전체 수로 보고하지 않는 기준
로컬 `.reports`는 재실행 자료이며 공개 원격의 정확한 candidate·run·artifact가 CI 근거
JUnit parser는 구조·case·종료 코드·시간을 확인하고 보고서 출처의 진위를 독립 인증하지 않는 범위

## 독립 리뷰와 수정

고정 기능 후보의 소스를 stdin으로 제공한 별도 native Codex 읽기 전용 실행 두 개에서 검토
거부된 shell 파일 읽기를 재시도하거나 권한을 낮추지 않고 허용된 입력을 제공한 방식
실행 전후 후보·트리 동일, 앞선 동일 read-only 설정의 canary 쓰기 거부 관측
현재 두 검토에 확인된 코드 결함은 없으며, 최신 결과·정확한 인계 경로 연결 지적을 이 기록과 각 change의 handoff에 반영
source snapshot에서 생략한 lock 본문·upstream object는 리뷰어의 확인 범위에서 제외하고 별도 무결성 검사로 확인

수정한 구체적 결함

- OpenSpec 후속 update의 전역 profile 영향: 새 격리 설정에서 7개 유지, 기존 설정 바이트 보존
- Git assume-unchanged·skip-worktree의 숨긴 변경: 실제 실패 회귀 후 후보 BLOCKED 처리
- 명세 sync/archive의 전달 순서와 무진전 반복: 제품 전달 정책·재고정·영향 재검사·repair/retry 중단 조건 명시
- Streaming 과거 영상 오인: 실제 디코딩 픽셀의 epoch 표식 검증, 새 hash의 과거 red 영상도 거부
- 종료한 부모의 자식 누락: 소유 Job Object·process group 정리, 살아 있는 자식·다른 작업 보존 검사
- 도구 권한 부재·빠른 outage 응답: BLOCKED 구분과 전체 2초 부재 확인

리뷰의 두 축은 실행된 사실과 실제 환경 제약을 구분하여 기록
stdin 소스 검토는 Codex Desktop의 자연어 자동 스킬 선택과 제품 명령 전체 실행을 대신하는 인수 근거로 사용 제외

## CI와 인계

첫 [CI 실행](https://github.com/tttaliesin/agent-harness/actions/runs/35724708653)은 Linux 검사를 통과하고 Windows 결과 폴더 부재로 실패
실패를 보존하고 폴더 생성만 수정한 [후속 실행](https://github.com/tttaliesin/agent-harness/actions/runs/35725047006)의 결과·artifact 대조 완료
후속 실행의 두 job 모두 SUCCESS 확인: artifact의 유지보수 117 case·OpenSpec 5·HTTP 12·Edge 7, 모두 failures/errors/skipped 0
Streaming artifact는 source candidate `d06fb7929b77837d159b2178188930a3ad5e3c65`, outage 2.0초·복구 2.141초·WebRTC decoded +27·cleanup PASS 확인

각 fixture의 OpenSpec change에 handoff·검사 위치·후보·수정 지적·다음 동작 기록
기록을 제공받은 독립 native 검토가 저장소·과거 후보·근거·다음 검사를 식별했고, 부족했던 최신 후보와 결과 경로 보완
명세와 tasks의 실제 validate·canonical sync/archive 결과는 해당 fixture의 OpenSpec 기록 참조
최종 공개 SHA와 최신 CI URL은 현재 task의 최종 인계 문서에 고정하여 전달

## 아직 완료하지 않은 원문 인수

- 사용자 설치 R2: 직접 수정 보존·백업·선택 전환·복구·중복 공급 정리·실제 Desktop 발견과 자동 호출
- Allsen: 실제 제품 변경·기존 명령·제품 CI·인계, 제품 RTSP→추론→WebRTC 전달
- GPU·tracker: 실제 GPU 추론·모델 출력·프레임 상관·정한 단절 정책의 객체 ID 확인
- PR: 실제 중복 이벤트·동시 writer 경합 시험; 현재는 event/head 재조회·no-op·단일 담당 절차와 routing 검토
- 운영: runner crash/종료, deploy 승인·잘못된 대상 거부·건강 실패·복구 시험

상세 선정 7+7+4·공통 5기능·3분야·2예제·H01–H26는 [요구 추적](requirements-coverage.md)에서 유지
필수 자원 부재는 BLOCKED, 미실행은 NOT_RUN, 실패는 FAIL로 남기는 기준
공급 수·선택 설치·두 실행 예제의 성공을 원문 전체 인수 완료로 확대하는 보고 제외

## 완료된 명세

- [Web/API 정본](../../fixtures/web-api/openspec/specs/web-api/spec.md)·[보관 기록](../../fixtures/web-api/openspec/changes/archive/2026-09-22-accept-web-api/handoff.md)
- [Streaming 정본](../../fixtures/streaming/openspec/specs/streaming/spec.md)·[보관 기록](../../fixtures/streaming/openspec/changes/archive/2026-09-22-accept-streaming/handoff.md)

각 change의 3개 요구를 실제 CLI로 반영·보관하고 strict validate 통과, canonical 요구 본문이 승인된 delta와 같은지 대조
