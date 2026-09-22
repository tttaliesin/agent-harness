# JUnit 결과 확인

## 실행과 결과 연결

제품의 기존 pytest 명령에 `--junitxml` 출력 위치를 지정하고 실제 종료 코드를 보관
아래는 이미 잠긴 환경을 준비한 uv 제품의 PowerShell 예시
`$checker`에는 설치된 `python-testing/scripts/check-junit.py`의 실제 경로 지정
검사기의 상대 경로 기준은 제품 저장소가 아닌 설치된 스킬 디렉터리

```powershell
$checker = '<INSTALLED_SKILL_DIRECTORY>/scripts/check-junit.py'
$runStart = uv run --frozen --no-sync python -c 'import time; print(time.time())'
uv run --frozen --no-sync python -m pytest --junitxml=.reports/python.xml
$testExit = $LASTEXITCODE
uv run --frozen --no-sync python $checker --report .reports/python.xml --exit-code $testExit --started-at $runStart
if ($LASTEXITCODE -ne 0) { throw 'Python test evidence rejected' }
```

`--started-at`은 실제 검사 직전에 같은 파일 시스템 시계 기준으로 채집한 Unix 초
실행별 새 경로와 실행 로그 병행 사용 권장
mtime 비교만으로 보고서 위조·다른 후보의 결과·원격 CI 출처 증명 불가
다른 호스트에서 옮긴 보고서는 현지 복사 시간을 실행 시간으로 해석하지 않고 해당 CI의 원본 실행 근거 확인

## CLI 계약

필수 입력 3개와 stdout JSON 출력
보고서 쓰기·의존성 설치·테스트 명령 실행 기능 없음

| 입력·결과 | 의미 |
| --- | --- |
| `--report PATH` | 현재 실행의 JUnit XML 파일 하나 |
| `--exit-code INTEGER` | 실제 테스트 프로세스 종료 코드 |
| `--started-at SECONDS` | 실제 실행 직전의 유한한 양수 Unix 초 |
| 종료 코드 `0` | 보고서와 명령 결과의 일관성 확인; `tests`, `executed`, `skipped`, `failures`, `errors` 제공 |
| 종료 코드 `1` | 읽기·내용·결과·신선도 거부; `status: FAIL`, `reason` 제공 |
| 종료 코드 `2` | 인자 누락·형식 오류; argparse 진단 |

필수 검사가 여러 보고서로 나뉘면 각 보고서와 해당 실행 코드·시작 시간에 검사기 적용
다른 보고서의 성공으로 실패·누락·미실행 검사 상쇄 금지

## 허용 범위와 실패 조건

- `testsuite` 또는 `testsuites` 루트와 실제 `testcase` 요소 필요
- 중첩 suite의 testcase를 각각 한 번만 집계; 상위 집계값을 별도 테스트로 합산하지 않는 방식
- 선언된 `tests`, `failures`, `errors`, `skipped` 값이 있으면 해당 하위 testcase 집계와 대조
- case당 failure/error/skipped 종류를 기준으로 집계; 같은 case의 상충 결과 거부
- 누락·비정상 XML·가짜 PASS 문자열·숫자만 있는 보고서·0 cases·모두 skipped·failure·error·실패 종료 코드 거부
- 이전 실행 mtime의 보고서 거부; 파서가 성공해도 필수 skipped 검사는 완료 근거에서 제외
- 8 MiB 이하, XML 깊이 64 이하, 요소 100,000개 이하만 처리
- UTF-8·UTF-16 포함 DTD를 선언 시작 시점에 거부하여 entity 확장 차단
- namespace 확장·생산자별 독자 구조·요약 전용 보고서는 이 검사기의 지원 범위 밖

XML parser의 보안 특성은 [Python XML 공식 문서](https://docs.python.org/3/library/xml.html) 참조
pytest 보고서 생성 옵션은 [pytest JUnit XML 공식 문서](https://docs.pytest.org/en/stable/how-to/output.html#creating-junitxml-format-files) 참조
