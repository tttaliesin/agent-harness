# `governance/` 운영 규칙

이 문서는 `governance/`에 두는 규칙의 이상적인 역할을 정한다.

## Workspace 전체에 적용하는 규칙을 둔다

`governance/`에는 category 경계, 공통 작업 원칙, repository에 공통으로 적용할 기준을 둔다.
또한 여러 repository를 가로지르는 Project의 목표·범위·결정·상태, 지속 책임의 현재 정책, 재사용할
workspace 지식의 정본을 둔다. 이 규칙과 지식은 특정 product의 기능, 특정 service의 실행 방식,
또는 개인 개발 환경을 정의하지 않는다.

공통 지식의 문서 형식·배치·수명주기는 해당 지식을 소유한 저장소에서 정의
작업 맥락과 지식 소유권은 [작업 안내](../use-cases.md)에 따라 확인

사용자가 선택한 공통 Harness에서는 category·소유권·승인 경계와 범용 개발 스킬을 `tools/agent-harness`의 한 패키지로 관리
정책 본문은 workspace-governance·development-tooling·github-actions-workflows 각 소유 스킬의 references에 배치
특정 시스템의 운영 스킬은 해당 구현 저장소에서 관리하며 같은 정책의 두 번째 원본을 만들지 않는 기준
범용 Markdown·GitHub 실행 절차와 workspace의 정책 내용은 같은 패키지 안에서 역할별로 구분

## 다른 category가 구현한다

`governance/`는 별도로 소유할 지식·결정이 있을 때 사용하는 category이며 공통 Harness 정책을 복제하는 별도 repository 생성 근거가 아님
실제 product 기능은 `products/`, 공통 실행 기반은 `infra/`, 개발 도구는 `tools/`에서 관리
Source code, configuration, test, 분석, 실행 결과는 대응 repository 또는 자료 소유 시스템에서 관리

새 규칙은 기존 category 운영 규칙과 모순되지 않아야 한다. 공통 규칙이 바뀌면 영향을 받는
category 운영 규칙도 함께 고친다.

## 개발 도구 정책

공통 runtime·package manager·task runner의 선택 기준과 적용 skill은 [개발 도구 기준](https://github.com/tttaliesin/agent-harness/blob/main/skills/development-tooling/references/development-tooling.md)이 소유한다.
정책을 전달하는 선언 템플릿은 이 저장소에 두고, 실제 버전·명령은 각 저장소, 공통 image·bootstrap 구현은 `infra/`, 개인 설치·설정은 `tools/`가 소유한다.
