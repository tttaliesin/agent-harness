# 공통 스킬 공급 구조 전환

2026-09-22 사용자 요청에 따라 npx skills 선택 설치 중심으로 변경
이번 저장소 정리는 R1, 사용자 설치 전환과 실제 사용 검증은 R2·R3에서 별도 수행

## 현재 저장소와 기존 설치

공급 원본을 root skills의 19개로 정리하고 전용 실행 CLI·Adapter schema·binding·역할 template·플러그인 3개의 원본 공급 종료
직전 구조는 Git commit 2d0d4bdd0a4e3b854c1745725e4523c27f882733에서 확인 가능
현재 사용자 설정과 설치 cache는 이 소스 변경으로 자동 갱신되지 않는 상태

## 9개 독립 스킬의 종료

| 종료한 스킬 | 필요한 절차의 소유자 |
| --- | --- |
| project-bootstrap | development-tooling의 기존 제품 조사·도구 확인 |
| project-workflow | 실제 명세·해당 구현 스킬·verification-before-completion |
| project-review | code-review의 후보 확인·두 축 검토·실제 권한 경계 |
| project-pr-followup | github-operations의 명시된 PR 후속 작업 |
| project-handoff | github-operations의 인계 참고 자료 |
| setup-matt-pocock-skills | Skills CLI 설치와 development-tooling |
| grill-with-docs | grilling의 결정 기록 참고 자료 |
| writing-for-agents | markdown-authoring 참고 자료와 사용 가능한 skill-creator |
| receiving-code-review | code-review의 피드백 검증 참고 자료 |

## 설치 전환 순서

1. 실제 설치 위치·출처·플러그인 설정과 직접 수정한 파일을 비교·백업
2. 시험 위치에서 선택 설치·반복 설치·갱신·복구 확인
3. 필요한 스킬을 새 공급에서 설치하고 내용과 발견 여부 확인
4. 대체된 항목에 한해 workflow-core·matt-engineering·superpowers-execution 중복 공급 비활성화
5. 실제 Codex 작업에서 이름별 공급 하나와 정상 호출 확인

이 순서는 이후 설치 작업용 안내이며 R1에서 실행 완료한 기록이 아님
권한·trust 화면은 실제 앱 절차에 따라 처리하고 소스 변경으로 승인된 것으로 간주 제외
미사용 로컬 .venv·dist·과거 .harness 결과는 다른 작업 소유 여부 확인 후 별도 정리

## 남은 검증

동일 revision의 공통 스킬을 Web·Python 예제와 Streaming 예제에서 실제 사용
Allsen에서는 기존 Taskfile·CI·명세로 실제 변경·리뷰·인계 검증
runner·배포의 승인·대상·실패 복구는 해당 운영 저장소에서 확인
스킬 공급 성공으로 CI 강제·읽기 전용 권한·중복 실행 방지·운영 인수를 통과 처리하는 방식 제외
