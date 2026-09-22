# 공통 스킬 공급 구조 전환

2026-09-22 사용자 요청에 따라 npx skills 선택 설치 중심으로 변경
현재 통합 소스는 공통 22개와 두 fixture별 OpenSpec 생성 7개로 구성
구현·관측·미완료의 기준은 [요구 대조](implementation/requirements-coverage.md)와 [기능 인수 기록](implementation/functional-acceptance.md) 참조

## 현재 저장소와 기존 설치

R1의 19개 공급에 project-workflow·python-testing·streaming-testing을 추가한 현재 22개
전용 실행 CLI·Adapter schema·binding·역할 template·플러그인 3개의 원본 공급 종료는 유지
직전 구조는 Git commit `2d0d4bdd0a4e3b854c1745725e4523c27f882733`에서 확인 가능
현재 사용자 설정과 설치 cache는 이 소스 변경으로 자동 갱신되지 않는 상태

OpenSpec은 [고정 CLI의 초기 구성·갱신 절차](../skills/development-tooling/references/openspec-setup.md)로 각 제품에 생성하는 별도 공급
공통 22개에 복사해 중복 설치하는 방식 제외
선택 설치와 native catalog 발견의 관측을 사용자 설치 R2 완료로 처리하지 않는 기준

## 기존 독립 스킬의 공급 변경

이전 9개 이름 정리 중 project-workflow는 작업 진행 연결을 맡는 독립 스킬로 복원
나머지 이름의 통합은 소유 위치를 뜻하며 원문 기능의 실제 인수 완료와 별개

| 기존 이름 | 현재 공급·필요한 절차의 소유자 |
| --- | --- |
| project-bootstrap | [development-tooling 초기 구성](../skills/development-tooling/references/openspec-setup.md) |
| project-workflow | [독립 스킬로 공급](../skills/project-workflow/SKILL.md), 기존 승인·OpenSpec·제품 명령·리뷰·인계 연결 |
| project-review | [code-review](../skills/code-review/SKILL.md)의 후보 검사·Spec/Standards·실제 권한 확인 |
| project-pr-followup | [github-operations](../skills/github-operations/references/followup-and-handoff.md)의 지정 PR 후속 절차 |
| project-handoff | [project-workflow 재개](../skills/project-workflow/references/followup-and-resumption.md)와 GitHub 인계 절차 |
| setup-matt-pocock-skills | Skills CLI 선택 설치와 development-tooling의 기존 tracker·문서·OpenSpec 7개 구성 |
| grill-with-docs | [grilling 결정 기록](../skills/grilling/references/record-decisions.md) |
| writing-for-agents | [markdown-authoring 참고 자료](../skills/markdown-authoring/references/writing-for-agents.md)와 사용 가능한 skill-creator |
| receiving-code-review | [code-review 피드백 검증](../skills/code-review/references/receiving-review.md) |

## 설치 전환 순서

현재 단계는 기능 구현·통합 검사와 실제 호출 인수
사용자 설치 R2는 아래 실제 관측이 준비된 항목부터 별도로 진행할 단계

1. 실제 설치 위치·출처·플러그인 설정과 직접 수정한 파일을 비교·백업
2. 시험 위치에서 선택 설치·반복 설치·갱신·복구 확인
3. 필요한 공통 스킬과 제품에서 생성할 OpenSpec 7개를 구분하여 내용·발견·실제 호출 확인
4. 대체된 항목에 한해 workflow-core·matt-engineering·superpowers-execution 중복 공급 비활성화
5. 실제 Codex 작업에서 이름별 공급 하나와 정상 호출 확인
6. 같은 revision의 두 예제를 새 설치본으로 재실행하고 설치 경로 변경에 따른 회귀 확인

이 순서는 이후 사용자 설치 작업용 안내이며 현재 R2 실행 완료 기록이 아님
권한·trust 화면은 실제 앱 절차에 따라 처리하고 소스 변경이나 canary 쓰기 거부만으로 전체 실행 승인·인수 판정 제외
미사용 로컬 .venv·dist·과거 .harness 결과는 다른 작업 소유 여부 확인 후 별도 정리

## 남은 검증

OpenSpec CLI 1.13.1의 생명주기 5개와 두 fixture strict validate 통과, candidate helper 10개 통과 관측
Web/Python worker 검사·MCP DOM·Streaming CPU/WebRTC 관측은 [기능 인수 기록](implementation/functional-acceptance.md)에 보존
통합 Web 재실행은 Python 12개·Edge 7개·두 JUnit 판정·cleanup·source/locks 보존 확인, root 회귀 39개 PASS 관측
실행 시점은 working HEAD `481f6a8`과 미커밋 docs/core 변경 포함; 최종 후보의 통과 근거로 자동 승격 제외
Streaming epoch·cleanup·outage 수정과 고정 후보 재실행 완료; 독립 native 리뷰·인계 보완·CI 상세는 기능 인수 기록

native 읽기 전용 canary 쓰기 DENIED 확인 후 허용된 stdin 소스 입력으로 분리된 두 native 리뷰 실행·트리 보존 확인
이 리뷰는 제품 명령 실행이나 사용자 Desktop 자동 선택 인수와 구분
거부된 읽기 재시도·권한 약화·우회로 전환을 완료하는 방식 제외

Allsen의 기존 Taskfile·CI·명세를 통한 실제 제품 검증과 GPU·tracker·운영 runner·배포·복구는 별도 인수
스킬 공급 성공을 CI 강제·읽기 전용 전체 실행·중복 실행 방지·운영 인수의 통과로 취급하는 방식 제외
