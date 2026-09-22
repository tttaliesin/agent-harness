# 브라우저 재현과 저장된 검사

## MCP 탐색·재현

기존 브라우저 세션을 요청한 작업에서는 해당 세션·승인 범위 유지
허용된 로컬 fixture 검증에서만 별도 격리 세션 사용
MCP 미설치 시 기존 연결·버전·필요 범위를 확인하고 승인된 로컬 의존성으로 연결
전역 설정 변경 없이 프로젝트에 설치된 CLI를 stdio로 실행하는 방식 사용 가능

프로젝트가 `@playwright/mcp@0.0.82`를 고정 설치하고 Edge를 갖춘 경우의 stdio 서버 실행 예시

```sh
node node_modules/@playwright/mcp/cli.js --isolated --headless --browser msedge --output-dir .reports/mcp --timeout-navigation 10000 --timeout-action 5000
```

이 명령은 MCP 서버 시작이며 테스트 통과 결과가 아닌 상태
연결할 MCP client의 지원 방식과 실제 `tools/list` 입력 schema 확인 필요
브라우저·버전 선택은 제품의 기존 설정 우선
[Playwright MCP 공식 안내](https://github.com/microsoft/playwright-mcp)의 격리 세션과 CLI 옵션 참조

1. stdio `initialize` 요청·응답, `notifications/initialized`, `tools/list`로 연결과 실제 도구 확인
2. 소유권과 readiness를 확인한 로컬 URL로 `browser_navigate` 실행
3. 반환 DOM snapshot에서 실제 입력·버튼·권한 상태 확인; snapshot이 파일 링크이면 해당 반환 파일 확인
4. 발견한 ref와 도구 schema로 입력·클릭·기다리기 수행; 화면 상태와 HTTP 결과·console 오류 대조
5. URL·계정 fixture·재현 단계·기대 결과·실제 결과·실행 브라우저 기록
6. 자신이 연 브라우저를 `browser_close`로 닫고 소유 stdio 연결·서버 프로세스 종료 확인

새 권한을 얻기 위한 별도 세션 우회·사용자 프로필 복제·전역 MCP 설정 변경 제외
실제 비밀 대신 제품이 승인한 테스트 계정 사용; 공개 loopback fixture 토큰은 실제 인증 검증과 별도 범위

## Playwright Test 수용 근거

재현된 요구를 제품의 기존 테스트 디렉터리·설정 안에 저장
새 설정이 승인된 경우에도 base URL·계정 fixture·정상/입력/권한/서비스 오류 경로를 명시
역할·label locator와 기대 DOM 상태를 사용하고 실제 필요한 HTTP 결과까지 확인
`retries: 0`으로 최초 실패를 보존하거나 제품의 재시도 정책과 flaky 결과를 명시적으로 기록

```sh
node node_modules/@playwright/test/cli.js test
```

검사 전의 실행 시작 시각, 실제 종료 코드, 현재 후보, 브라우저·버전, 실행·실패·skipped 수, 보고서 경로를 함께 기록
반환 코드 0만으로 통과 판정 금지; 누락·0 cases·모두 skipped·보고서 실패도 실패 근거
필수 브라우저 부재는 BLOCKED로 남기고 Python/API 결과로 대신 통과 처리하지 않는 기준
다른 브라우저·실제 제품·실제 계정은 실행하지 않았다면 미검증으로 유지

서버 시작은 승인된 소유 프로세스에 한정하고 기존 서버 재사용 시 주소·애플리케이션 identity까지 검증
fixture처럼 전용 서버를 띄우는 검사는 `reuseExistingServer: false`로 다른 실행과의 충돌을 명시적 실패로 처리
Windows 등에서 종료 권한이 없으면 남은 소유 PID·명령을 기록하고 권한 있는 담당자가 정확한 프로세스만 정리
[Playwright webServer 공식 문서](https://playwright.dev/docs/test-webserver)와 [설치된 Chrome·Edge 사용 안내](https://playwright.dev/docs/browsers#google-chrome--microsoft-edge) 참조
