# 선별 upstream과 통합

정확한 저장소·commit·license는 [서드파티 안내](../THIRD_PARTY_NOTICES.md), 파일별 적용 내역은 upstream.lock.json에서 관리
원본 Git object·선별 파일·patch는 provenance 아래 보존

현재 목록은 R1의 공급 기록이며 원문 전체 선정·기능 충족은 [요구 대조](implementation/requirements-coverage.md)에서 별도 판정

## OpenSpec

원문 선정 7개는 고정 OpenSpec CLI가 제품 .agents/skills에 생성하는 공급 경로 유지
공통 19개에 포함되지 않으며 제품에서의 명세→구현→검증→정본 반영→보관 연결 미완료

## Matt Pocock

domain-modeling·grilling·codebase-design·code-review 네 스킬을 root skills로 공급
grill-with-docs의 결정 기록은 grilling 참고 자료로, writing-for-agents의 지침은 markdown-authoring 참고 자료로 통합
setup-matt-pocock-skills의 독립 공급 종료; 실제 제품 초기 구성의 대체 절차는 미완료
통합한 세 이름의 기능 보존을 파일 이동만으로 완료 처리한 판단 정정

## Superpowers

test-driven-development·verification-before-completion 두 스킬 공급
receiving-code-review의 근거 확인 절차는 code-review 참고 자료로 통합
기존 systematic-debugging 수정본은 같은 이름의 단일 공급 유지

## 로컬 변경

제품 연결 CLI·Core workflow 전제를 제거하고 현재 작업·제품 명세·기존 명령 사용
스킬의 직접 호출 조건과 관련 자료를 보존하고 선택 설치에 필요한 license 함께 포함
일반 정책·기존 스킬의 저작권과 license는 기존 자료에 따라 유지
artifact hash 범위에 포함됐다는 이유만으로 다른 license를 일괄 적용하는 방식 제외
