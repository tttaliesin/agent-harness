# `products/` 운영 규칙

사용자·고객에게 제공하는 기능과 경험을 소유하는 저장소 분류

## Product source와 image를 소유한다

Source·모듈 image·application configuration·health interface를 제품 저장소에서 관리
모듈별 독립 version과 변경 범위에 맞는 검증·발행 허용
설정 이름·타입·필수 여부·기본값과 image 내부 asset은 Product 계약에 포함
제품별 module 목록·수량·발행 metadata·명령은 해당 저장소에서 확인

Runtime Compose·service 연결·network·volume·target binding의 소유자는 실제 실행과 운영 책임으로 판단
Product의 로컬·통합 테스트 fixture와 Compose 제공 허용
가능한 모든 배포 topology를 Product가 미리 정의하도록 요구하지 않는 원칙

공통 application 서비스는 `platforms/`, 실행·배포 기반은 `infra/`, 개발 도구는 `tools/`, 원천 자료는 `data/`의 interface를 소비
다른 구성요소의 내부 구현이나 현재 상태를 제품 분류 규칙에서 재정의하지 않는 원칙

## 제품 발행과 운영 연결

Product CI의 검증·발행·moving channel 정책은 [Actions 규칙](https://github.com/tttaliesin/agent-harness/blob/main/skills/github-actions-workflows/references/github-actions-workflows.md#product-ci-build-only-계약) 적용
배포 실행은 대상 저장소의 현재 계약을 확인하며 발행 성공과 실제 실행 결과를 구분
Product build에 배포·host 관리 자격 증명을 공급하지 않는 경계 유지
Runtime 연결 방식·실행 기반·권한은 [Infra 규칙](infra.md)을 적용하고 실제 작업 대상은 [소유 스킬 안내](../../../../SKILL.md#route-by-responsibility)에서 선택
