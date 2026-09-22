# 제품 발행과 Komodo 운영 흐름

제품 source 변경 → GitHub Actions 검사·이미지 발행 → GHCR immutable 이미지·검증된 테스트 channel
Deploy 설치 릴리스 → 기존 digest 조합의 설치 검사 → GitHub Release의 release.json·설치 파일
고객 운영 TOML 변경 → Git 검토·병합 → 승인된 설치 적용 Action → Sync·config 반영·Stack Deploy·health 확인

## 책임

| 시스템 | 수행 |
| --- | --- |
| Product Actions | Source 검사·독립 이미지 발행·발행 사실 알림 |
| Deploy Git·Actions | 배포 Compose·설치와 선택한 upgrade 검사·설치 릴리스·고객 설정 |
| Komodo | 리소스 diff·Sync·Compose 배포·조회·실행 이력 |
| Ansible | Core·MongoDB·Periphery와 호스트 설정 |
| Self-hosted runner | 제품 build·호스트 구성 실행 기반 |

자동배포 설치는 발행·deploy 변경 이벤트로 갱신하고 고객 설치는 digest 고정과 명시적 배포
자동배포 등록·전달·재처리는 deploy의 [발행 이벤트 계약](https://github.com/suchang-busan/deploy/blob/main/docs/publication-events.md)에서 확인
제품별 Compose·service 수·현행 운영 상태는 해당 구현 저장소에서 확인

## 시작 문서

- [Deploy 설치 릴리스](https://github.com/suchang-busan/deploy/blob/main/products/README.md)
- [Komodo 운영](https://github.com/suchang-busan/deploy/tree/main/management/komodo)
- [호스트 Ansible](https://github.com/suchang-busan/deploy/tree/main/hosts/ansible)
- [Runner 운영](https://github.com/suchang-busan/self-hosted-runner)
- [CI·릴리스 책임 경계](../skills/github-actions-workflows/references/github-actions-workflows.md)
