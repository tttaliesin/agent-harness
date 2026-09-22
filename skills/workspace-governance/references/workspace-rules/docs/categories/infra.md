# Infra

실행 기반·공통 runner·관리 시스템·고객 설치 운영의 구현 저장소 영역

## 소유권

Product는 제품 코드·Dockerfile·이미지 발행·실행 계약 담당
Deploy는 배포 Compose·지원 값·설치별 설정·설치 검사와 릴리스·native Komodo 리소스·Ansible 관리 기반 담당
Self-hosted runner는 공통 이미지·등록 entrypoint·역할 Compose 담당
앱 배포와 실행 이력은 Komodo, 소스·릴리스 발행은 GitHub Actions 담당

## 호스트와 권한

호스트·Docker Engine·SSH host key·Periphery 공개키는 실제 연결에서 검증된 identity 사용
Core·Periphery의 연결 방향은 해당 설치의 네트워크 조건으로 결정
Core loopback UI 공개나 특정 overlay network를 모든 고객의 필수 조건으로 요구하지 않는 방식

Product CI와 호스트 구성 runner의 repository scope·시크릿·capability 분리
Persistent runner에서 untrusted PR 코드 실행 금지
Product build는 job별 격리 builder, 호스트 구성은 선택한 target의 SSH interface 사용
Komodo Periphery의 Docker socket은 해당 Engine 전체 관리 권한이며 단순한 서비스 분리로 기술적 격리를 주장하지 않는 경계

## 운영과 복구

관리 기반은 owner의 Compose·Ansible과 host 시작 adapter 사용
소스는 Git 이력, DB·키·시크릿·운영 데이터는 checkout 밖의 보관 정책 적용
Engine·관리 시스템·앱 데이터의 손실 경계를 구분하고 실제 복구 검증 범위만 완료로 보고
OS·Docker 준비의 지원 범위는 현재 호스트 관리 구현에서 확인하고 실제 수행·검증한 범위만 자동화 완료로 보고

Portainer·전용 배포 runner·Actions 앱 CD는 이 운영 모델의 필수 요소에서 제외
이미 이관한 관리 기능의 이전 구현은 활성 복사본 없이 Git 이력에서 조회
상세 CI·릴리스·운영 책임은 [Actions 정책](https://github.com/tttaliesin/developer-skills/blob/main/skills/github-actions-workflows/references/github-actions-workflows.md) 참조
