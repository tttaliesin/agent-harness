# Web/API 실행 fixture

Python 표준 라이브러리 HTTP 서버와 저장된 Playwright Test로 Web·Python 검사 연결 확인
실제 제품·배포·실제 계정의 통과 근거와 별개
요구·OpenSpec·리뷰·인계 연결 파일은 통합 담당자가 추가할 대상

## 환경 준비

작업 디렉터리는 `fixtures/web-api`
Python 3.12+, uv, Node.js, npm, 설치된 Edge 또는 Chrome 필요
확인한 버전은 [실행 기록](RUN-EVIDENCE.md) 참조
아래 설치 명령은 fixture의 `.venv`·`node_modules`만 구성하며 검사 명령과 별도 실행

```powershell
$env:UV_CACHE_DIR = Join-Path (Get-Location) '.reports/uv-cache'
$env:UV_PYTHON_DOWNLOADS = 'never'
$env:npm_config_cache = Join-Path (Get-Location) '.reports/npm-cache'
$env:PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD = '1'
uv sync --locked
npm ci --ignore-scripts --no-audit --no-fund
```

시스템 Python 자동 선택이 불가능하면 `uv sync --locked --python <AVAILABLE_PYTHON>`으로 실제 읽기 가능한 interpreter 지정
Windows 실행 권한 제한 환경에서는 uv 실행·소유 서버 종료가 가능한 동일 작업 소유자로 실행
브라우저가 없으면 필수 브라우저 검사는 BLOCKED; 다른 검사 성공으로 대체 불가
의존성 설치·검사 옵션의 의미는 [uv 동기화 공식 문서](https://docs.astral.sh/uv/concepts/projects/sync/) 참조

## Python 검사와 보고서 확인

저장소 경로의 검사기 사용 예시
선택 설치한 스킬에서는 `$checker`를 해당 설치 디렉터리의 같은 파일로 변경
다른 환경에서도 검사기 본문 변경 없이 같은 인자 사용

```powershell
$checker = '../../skills/python-testing/scripts/check-junit.py'
$runStart = uv run --frozen --no-sync python -c 'import time; print(time.time())'
uv run --frozen --no-sync python -B -m pytest -p no:cacheprovider --junitxml=.reports/python.xml
$testExit = $LASTEXITCODE
uv run --frozen --no-sync python -B $checker --report .reports/python.xml --exit-code $testExit --started-at $runStart
if ($LASTEXITCODE -ne 0) { throw 'Python fixture evidence rejected' }
```

실제 HTTP 테스트 12개, 각 실행이 동적 포트의 소유 서버를 시작하고 종료하는 구성

## 브라우저 검사와 보고서 확인

`FIXTURE_PORT`는 해당 worktree 전용 빈 포트 선택; 기본값 `8765`
서버는 항상 `127.0.0.1`에만 바인딩하고 기존 포트가 사용 중이면 실패
Windows 기본 channel은 `msedge`, 다른 OS 기본값은 `chrome`
저장된 테스트 7개와 각 테스트 전 `/health` 애플리케이션 identity 확인

```powershell
$env:FIXTURE_PORT = '19387'
$env:FIXTURE_BROWSER_CHANNEL = 'msedge'
$checker = '../../skills/python-testing/scripts/check-junit.py'
$runStart = uv run --frozen --no-sync python -c 'import time; print(time.time())'
node node_modules/@playwright/test/cli.js test
$testExit = $LASTEXITCODE
uv run --frozen --no-sync python -B $checker --report .reports/browser.xml --exit-code $testExit --started-at $runStart
if ($LASTEXITCODE -ne 0) { throw 'Browser fixture evidence rejected' }
```

Playwright가 소유 서버와 브라우저 종료 담당
동작 제한 시간 15초, assertion 5초, 전체 검사 60초, 서버 시작 10초, 재시도 0회
Windows 제한 계정에서 자식 프로세스 종료 권한 오류 발생 시 실패로 기록하고 실제 소유 PID·명령을 확인한 담당자가 해당 트리만 정리
다른 포트의 서버나 사용자 브라우저 일괄 종료 제외
생성물은 `.reports/`, `.venv/`, `node_modules/`에 한정

## 실제 경로와 공개 테스트 identity

응답과 화면의 일치 여부를 저장된 [Python 테스트](tests/test_api.py)와 [브라우저 테스트](e2e/flows.spec.cjs)에서 확인

| 경로·동작 | 기대 결과 |
| --- | --- |
| `/health` | `200`, `agent-harness-web-api` identity |
| `/api/greet?name=Ada` | `200`, `Hello, Ada!` |
| 빈 이름·40자 초과 | `422`, 입력 오류 |
| `/api/admin`, 토큰 없음·잘못된 토큰 | `401` |
| `/api/admin`, `Bearer public-fixture-viewer` | `403` |
| `/api/admin`, `Bearer public-fixture-admin` | `200` |
| `/api/error` | `503`, 화면 오류 표시와 다음 정상 요청 복구 |
| 없는 경로 | `404` |
| HTML 형태의 이름 | 화면에 문자 그대로 표시 |

토큰은 공개·고정·loopback fixture 전용 문자열이며 실제 계정 비밀과 별도
서버는 파일 저장·데이터베이스·외부 API 없이 요청별 응답만 제공

## MCP 재현

별도 terminal에서 `uv run --frozen --no-sync python -B app.py --port 19388`로 소유 서버 시작
첫 stdout JSON의 URL과 `/health` identity 확인 후 [Web 스킬의 MCP 절차](../../skills/webapp-testing/references/playwright-evidence.md) 적용
`node node_modules/@playwright/mcp/cli.js ...` 명령으로 프로젝트의 고정 MCP 사용 가능
이 fixture의 설치된 CLI는 `@playwright/mcp@0.0.82`
탐색 결과를 공식 Test 수에 합산하지 않고 재현 후 소유 브라우저·서버 종료

## 공통 스킬 무수정 재실행

다른 fixture와 동일한 공통 revision에서 위 명령과 같은 검사기 사용
fixture별 분기·공통 코드 수정 없이 제품 명령과 결과 경로만 변경
통합 수용 시 검사 전후 공통 파일 해시 비교와 현재 Git candidate를 함께 보관

```powershell
$commonPaths = @('../../skills/python-testing/scripts/check-junit.py', '../../skills/python-testing/SKILL.md', '../../skills/webapp-testing/SKILL.md')
$before = $commonPaths | Get-FileHash -Algorithm SHA256 | Select-Object Path, Hash
# 위 Python·브라우저 검사 실행 후 비교
$after = $commonPaths | Get-FileHash -Algorithm SHA256 | Select-Object Path, Hash
if (Compare-Object $before $after -Property Path, Hash) { throw 'Common skill files changed' }
```

보고서 거부 회귀 검사는 저장소 루트에서 아래 명령으로 실행
검사 대상은 CLI의 실제 입출력이며 고의로 만든 실패 보고서에 대한 성공 종료 거부 포함

```sh
python -B -m pytest -p no:cacheprovider tests/test_python_reports.py --basetemp=.reports/python-report-tests --junitxml=.reports/python-report-tests.xml
```
