# Web/Python 실행 기록

실행일: 2026-09-22
기준 commit: `650a7d90e0963f17aa0203a811f8f9055798b374`
대상: `codex/requirements-web-python`의 Web/Python 변경
아래는 로컬 worker 실행 근거이며 통합 후보·제품 인수 결과와 별개

## 실행 환경

- Windows, Python 3.12.14, uv 0.12.10, pytest 9.1.1
- Node.js 24.19.0, npm 12.0.2, Skills CLI 1.7.0
- Playwright Test 1.63.0, 설치된 Microsoft Edge 153.0.4234.48, headless
- Playwright MCP 0.0.82; 서버가 반환한 내부 Playwright 버전 `1.64.0-alpha-1789764292000`
- fixture 전용 uv 환경·npm 의존성 사용; 전역 MCP·브라우저 프로필 설정 변경 없음

## 관측한 결과

재실행 명령의 작업 디렉터리·환경 변수·보고서 검사 인자는 [사용법](USAGE.md) 참조

| 검사 | 실제 실행 결과 | 근거 위치 |
| --- | --- | --- |
| HTTP fixture | 12 passed, failures/errors/skipped 0 | `tests/test_api.py`, `.reports/python.xml` |
| 저장된 Edge Test | 7 passed, failures/errors/skipped 0 | `e2e/flows.spec.cjs`, `.reports/browser.xml` |
| JUnit CLI 회귀 | 29 passed | 저장소 `tests/test_python_reports.py`, `.reports/report-tests.xml` |
| 실제 Python·browser XML 판정 | 종료 코드·실행 직전 시간 포함 검사 성공 | `check-junit.py` stdout JSON |
| npx 선택 설치 | 두 스킬만 격리 디렉터리에 복사 설치 | `.reports/selected-install/.agents/skills/` |
| 설치된 독립 검사기 | `python -I -B`로 실제 생성 XML 판정 | 위 설치 디렉터리의 `python-testing/scripts/check-junit.py` |
| MCP stdio | initialize, tools/list 25개, 실제 Edge DOM 로딩, browser_close 성공 | `.reports/mcp-probe.json`, `.reports/mcp/` |
| 공통 소스 보존 | fixture 검사 전후 SHA-256 일치 | `.reports/common-hashes.json` |

`.reports`는 재생성 가능한 로컬 실행 산출물이며 Git 납품 파일에서 제외
표의 MCP 발견 수는 테스트 통과 수에 합산하지 않는 기준

## 실패를 관측한 뒤 수정한 항목

- JUnit 기능 구현 전 독립 설치·중첩 집계 2개 assertion 실패 확인
- HTTP handler 구현 전 실제 응답 `501`과 기대 `200/401/403/404/422/503`의 차이로 12개 테스트 실패 확인
- UI 요청 연결 전 Edge에서 HTTP 응답 대기 15초 시간 초과 확인
- XML의 알 수 없는 encoding 선언에 traceback 발생 재현 후 구조화된 FAIL로 처리; 전용 CLI 회귀 통과
- JUnit 누락·가짜 PASS 문자열·잘못된 XML·요약 숫자만 존재·0 cases·모두 skipped·failure·error·exit 0의 실패 보고서·실패 프로세스·stale·DTD·UTF-16 entity·크기/깊이 초과 거부 확인
- 중첩 suite의 실제 case 한 번 집계와 일부 skipped의 분리 집계 확인

최초 Windows 제한 실행에서 Playwright 자식 서버 종료가 차단되어 teardown 시간 초과와 잔류 포트 관측
당시 소유 PID·정확한 실행 명령 확인 후 해당 프로세스 트리만 종료
동일 작업 소유자 권한의 후속 실행에서는 Test 종료·소유 서버 정리까지 성공
이를 무조건 성공으로 덮지 않고 실행 권한 한계로 보존

## 근거의 한계와 통합 후 확인

- Edge 한 환경의 fixture 검사이며 Chrome·Firefox·WebKit·다른 OS·실제 제품 미검증
- npx 복사 설치와 설치 경로의 CLI 실행 확인; Codex Desktop의 자연어 자동 호출·skill loader 인수는 별도
- JUnit 검사기는 보고서 일관성과 명령 종료·mtime 신선도만 확인; 실제 CI 출처·보고서 위조·현재 candidate 귀속은 통합 workflow 담당
- OpenSpec 7개·공식 Spec/Standards 리뷰·다른 fixture와 동일 candidate 수용·handoff lifecycle은 통합 담당자 범위
- 전체 공통 패키지 검사·root provenance/lock 갱신·공개 push는 통합 담당자 범위
