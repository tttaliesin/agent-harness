# 선별 upstream과 통합

정확한 저장소·commit·license는 [서드파티 안내](../THIRD_PARTY_NOTICES.md), 파일별 적용 내역은 upstream.lock.json에서 관리
원본 Git object·선별 파일·patch는 provenance 아래 보존

현재 공통 22개와 제품·fixture별 OpenSpec 7개는 공급 경로의 구분
원문 7+7+4 선정과 통합한 기능의 범위는 [요구 대조](implementation/requirements-coverage.md), 실제 검사·남은 인수는 [기능 인수 기록](implementation/functional-acceptance.md)에서 판정

## OpenSpec

원문 선정 7개는 고정 OpenSpec CLI 1.13.1이 제품 .agents/skills에 생성하는 공급 경로 유지
선정 이름은 openspec-explore·openspec-propose·openspec-apply-change·openspec-update-change·openspec-verify-change·openspec-sync-specs·openspec-archive-change
공통 22개와 분리하여 Web/API·Streaming 각 fixture에 7개 생성

[development-tooling의 setup](../skills/development-tooling/references/openspec-setup.md)에서 custom profile과 7개 workflow를 명시하고 이후 update에도 임시 XDG 설정 적용
[실제 CLI 검사](../fixtures/openspec/test_lifecycle.py) 5개 PASS 관측: 반복 init·격리 update·canonical archive·잘못된 spec 거부·기존 문서 보존
기존 core profile·profile 미설정에서 새 세션으로 update한 뒤 사용자 설정 바이트와 생성 7개 보존 포함
두 fixture의 strict validate도 실제 CLI PASS 관측
이 결과는 OpenSpec 도구의 생명주기 검사이며 native Codex의 전체 구현·리뷰·인계 인수는 별도

## Matt Pocock

원문 선정 7개 중 domain-modeling·grilling·codebase-design·code-review 네 스킬을 root skills로 공급
나머지 세 기능의 현재 소유 위치는 아래와 같이 유지

| 원문 선정 | 통합 위치 | 보존할 행동 |
| --- | --- | --- |
| setup-matt-pocock-skills | [development-tooling setup](../skills/development-tooling/references/openspec-setup.md) | 기존 tracker·CLAUDE·AGENTS·도구·승인 회수와 OpenSpec 생성·발견 |
| grill-with-docs | [grilling 결정 기록](../skills/grilling/references/record-decisions.md) | 필요한 협의·결정 기록·domain-modeling 연결 |
| writing-for-agents | [markdown-authoring 참고 자료](../skills/markdown-authoring/references/writing-for-agents.md) | 에이전트용 문서의 필수 지침·참고 자료 구분 |

code-review의 [candidate helper](../skills/code-review/scripts/check-candidate.py)는 제품 검사·리뷰 권한을 실행하지 않는 읽기 전용 전제 검사
실제 hidden Git flags의 red→green을 포함한 10개 회귀 통과와 native 읽기 전용 실행 인수를 분리
통합한 이름의 파일 이동이나 helper 성공만으로 원문 행동 보존 완료를 선언하는 방식 제외

## Superpowers

원문 선정 4개 중 test-driven-development·verification-before-completion 두 독립 스킬 공급
기존 systematic-debugging 수정본은 같은 이름의 단일 공급 유지
receiving-code-review의 근거 확인·지원되는 수정·영향 검사는 [code-review 참고 자료](../skills/code-review/references/receiving-review.md)로 통합

## 로컬 변경

project-workflow·python-testing·streaming-testing을 추가하여 공통 작업 진행과 구체적인 보고서·미디어 검사를 연결
제품의 기존 명세·명령·CI를 사용하며 공통 실행 서비스·제품별 Adapter schema·binding 도구 추가 제외
두 fixture는 같은 공통 revision의 재사용 검증을 위한 예제이고 실제 제품·GPU·tracker·운영 결과와 별도

스킬의 직접 호출 조건과 관련 자료를 보존하고 선택 설치에 필요한 license 함께 포함
일반 정책·기존 스킬의 저작권과 license는 기존 자료에 따라 유지
artifact hash 범위에 포함됐다는 이유만으로 다른 license를 일괄 적용하는 방식 제외
root provenance·lock 검사는 실제 Linux CI에서 통과; 코드 리뷰와 fixture 결과를 해당 후보·run에 연결하는 기준 유지
