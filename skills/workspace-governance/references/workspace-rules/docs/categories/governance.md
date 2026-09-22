# `governance/` 운영 규칙

여러 저장소에 걸친 지식·결정에 독립 소유자가 필요한 경우 사용하는 category
현재 공통 작업 정책과 전달 스킬의 소유자는 `tools/agent-harness`

## 공통 정책의 소유권

Category·소유권·승인 경계는 Agent Harness의 workspace-governance 스킬에서 관리
개발 도구 기준은 development-tooling, 공통 CI 책임은 github-actions-workflows에서 관리
정책 본문은 각 소유 스킬의 `references/` 한 곳에 배치하고 README·소비 문서는 해당 원문으로 연결
범용 Markdown·GitHub 실행 절차도 같은 패키지 안의 담당 스킬에서 관리

특정 시스템의 운영 스킬과 현재 실행 계약은 해당 구현 저장소에서 관리
제품별 목표·범위·결정·상태는 제품 저장소, 운영 설정·절차·복구는 운영 저장소 소유
작업 맥락과 지식 소유권은 [작업 안내](../use-cases.md)에 따라 확인

## 지식과 구현의 배치

별도 소유할 지식·결정이 실제로 있을 때만 `governance/` 활용
공통 Harness 정책을 복제하는 별도 저장소나 상위 workspace 지침 파일을 만드는 근거로 사용하지 않는 기준
공통 지식의 형식·배치·수명주기는 해당 지식을 소유한 저장소에서 정의
제품 기능은 `products/`, 실행 기반은 `infra/`, 개발 도구는 `tools/`에서 관리
Source·configuration·test·분석·실행 근거는 이를 생산한 저장소 또는 자료 소유 시스템에서 관리

공통 규칙 변경 시 영향을 받는 category 규칙·참조도 같은 변경에서 갱신

## 개발 도구 정책

공통 runtime·package manager·task 진입점의 선택 기준과 선언 템플릿은 [개발 도구 기준](https://github.com/tttaliesin/agent-harness/blob/main/skills/development-tooling/references/development-tooling.md)의 소유 스킬에서 관리
실제 버전·명령은 각 저장소, 공통 image·bootstrap 구현은 `infra/`, 개인 설치·설정은 해당 도구 소유자 담당
