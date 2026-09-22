# GitHub Actions와 Komodo 운영 경계

제품 source 검사·이미지 발행·설치 릴리스 검증은 GitHub Actions, 앱 배포·운영은 Komodo, 호스트 구성은 Ansible 담당
현재 구현과 지원 구성·실행 명령은 각 소유 저장소에서 확인

## Repository와 역할의 소유권

| 책임 | 소유자 |
| --- | --- |
| 제품 source·Dockerfile·이미지 발행·실행 계약 | Product |
| 배포 Compose·지원 값·설치별 설정·설치 검사·release.json | Deploy |
| 고객별 Server·Stack·Resource Sync·실행 시점 | Deploy |
| Core·MongoDB·Periphery·호스트 설정 Ansible | Deploy |
| 공통 runner 이미지·실행 설정·등록 절차 | Self-hosted runner |
| 범용 workflow 보안과 workspace 책임 경계 | Developer Skills의 소유 정책 스킬 |

제품에 고객별 호스트·시크릿 값을 포함하지 않는 경계
운영 TOML의 image digest와 Compose 커밋은 선택한 deploy 설치 릴리스와 일치
고객별 추가 명세를 native TOML로 변환하는 계층과 별도 배포 상태 DB 미사용
Portainer API executor·Actions 앱 CD는 운영 경로에서 제외
Product의 발행 사실 알림은 허용하며 대상 선택·배포 실행은 deploy 소유 Komodo 경로에서 처리
이전 구현의 소스는 Git 이력에서 조회

## Product CI build-only 계약

PR source는 untrusted로 취급하고 GitHub-hosted runner에서 credentials 없는 검사 수행
검토·병합된 제품 source의 모듈별 build·test·이미지 발행은 Product CI 담당
변경 탐지는 제품 catalog와 이전 검증 발행을 사용하며 조회 실패를 unchanged로 처리하지 않는 방식
독립 모듈의 실패가 성공한 sibling 발행 결과를 무효화하지 않는 구조

각 이미지의 immutable tag·digest·source SHA·module identity와 provenance 검증
변경 없는 이미지 재사용 허용, 모든 이미지의 source SHA가 같다고 가정하지 않는 원칙
검증된 moving channel writer는 제품 CI로 제한
오래된 실행이 최신 channel을 되돌리거나 동일 발행 identity에 다른 digest를 덮어쓰지 않는 정책
Registry artifact·label·tag의 상세 형식은 제품 구현 소유

## 제품 설치 릴리스

Deploy가 소유한 공통 Compose는 이미지를 입력으로 받고 호스트별 값은 설치 설정에서 선택하는 구성
선택한 기존 digest 조합으로 격리된 설치 환경에서 health·제품 기능 확인 후 릴리스 발행
지원 구버전이 선택된 경우 해당 조합→후보 조합의 upgrade 검사
초기 릴리스나 미검증 경로를 upgrade 성공으로 기록하지 않는 원칙
release.json에 Compose 커밋·파일·service별 digest·각 source·지원 구성·검사 결과 기록
GitHub Release의 설치 파일과 명세를 운영 선택의 근거로 사용

## Event와 상태 전이

Source 검사·모듈 발행·릴리스 발행·Resource Sync·실제 Deploy·서비스 정상 확인은 각각 별도 결과
제품 발행 완료를 실제 설치 성공으로 표현하지 않는 기준
단일 스택은 Komodo Stack과 native hook, 여러 작업의 순서가 필요한 경우에만 Procedure 사용
자체 작업 큐·API wrapper·상시 상태 reconciler 미도입

## Product CI→automatic test refresh transport

자동 갱신 대상·이벤트 전달·재처리 방식은 deploy의 [현재 발행 이벤트 계약](https://github.com/suchang-busan/deploy/blob/main/docs/publication-events.md)에서 확인
현재 경로는 Product 이미지 발행과 deploy 검사 완료의 알림을 기존 Komodo Action으로 전달하는 방식
주기적 registry polling을 추가하지 않고 자동배포 등록·대상 선택은 deploy에서 관리
고객 운영 Stack은 digest 고정·수동 배포를 기본으로 사용
staging·production 명칭만으로 자동 갱신·접근 권한을 부여하지 않는 원칙

## Automatic test composition

Product는 이미지 실행 계약과 module catalog, deploy는 배포 Compose·선택한 이미지 조합·설치 검증 소유
운영자는 검증된 deploy 설치 릴리스와 설치 값·프로젝트·볼륨·네트워크 선택
이미지 발행 알림은 새 module의 배포 등록을 대신하지 않으며 구성 변경은 deploy Git 검토·검사·반영 필요

## Selected service composition 계약

운영자는 릴리스를 선택하고 고객 Stack의 commit·file_paths·image 환경 변수를 같은 명세에 맞춰 변경
PR 검토·검사와 병합 후 고객 작업 시간에 소유 저장소의 설치 적용 절차 실행
현재 설치 적용은 기존 native Action이 Sync·config 반영·Stack Deploy를 순서대로 처리하며 단계별 실패와 최종 상태 확인
Sync의 deploy=false와 고객 auto_update=false 유지
같은 Stack에서 설정 Sync와 Deploy를 동시에 실행하지 않는 운영 절차
제품 데이터·DB 호환성이 검증되지 않은 자동 rollback 미제공

## Runner와 untrusted code 경계

Product publication runner는 socketless와 job별 격리 builder 사용
호스트 Ansible runner는 선택한 호스트의 SSH와 호스트 연결 완료에 필요한 제한된 관리 권한만 사용하며 앱 배포 credential 미사용
PR 코드는 persistent trusted runner나 secret을 가진 job에서 실행하지 않는 원칙
pull_request_target에서 검사가 필요하면 trusted base의 검사 코드만 실행하고 후보 파일은 데이터로만 읽는 경계
후보 ref checkout·후보 코드 실행·후보 dependency 설치 금지
읽기 App token도 필요한 repository·최소 권한·단계에만 공급

## 관리 plane과 host bootstrap 계약

Core·Periphery 배치는 검증된 호스트·네트워크 도달성과 운영 필요로 선택
중앙 Core→고객 Periphery 또는 고객 내부 Core 구성 허용
Core UI 외부 공개를 모든 연결의 전제로 요구하지 않는 원칙
호스트 신뢰·Docker 연결 대상·공개키·시크릿은 현재 대상의 검증된 입력 사용
현재 구현에서 요구하지 않는 Engine ID를 별도 필수 입력으로 추가하지 않는 기준
Portainer bootstrap과 배포 runner를 Komodo의 필수 의존성으로 요구하지 않는 경계

Ansible은 호스트와 관리 기반 구성만 수행하고 Komodo 앱 API wrapper를 포함하지 않는 구조
현재 역할이 Docker 사전 설치를 요구하면 Docker 설치 자동화 완료로 표현하지 않는 기준
Windows adapter는 owner 정의의 host 경로·입력·시작을 연결하는 최소 실행 경로
DB·인증키·운영 데이터는 checkout 밖에서 보관하며 소스 이력과 구분
시크릿·공개키·복구 데이터의 보관과 실제 복구 가능 여부는 소유 시스템에서 별도 확인

## Evidence discovery and operation applicability

기존 승인 범위는 같은 대상·행위·환경에서 유지
소스·Git 병합·설정 반영·runtime 실행·기능 정상·불필요 권한 제거를 별도로 확인
일반 제품 기능과 자체 설정 검사는 실제 변경 위험에 맞춰 수행
검증된 외부 제품의 일반 동작을 다시 개발·검증하는 별도 체계 미도입
운영 도구 변경 시 실제 연결·선택 구성·실행 결과를 확인하되 불필요한 전체 환경 재검사 요구 금지
