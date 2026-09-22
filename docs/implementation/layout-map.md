# 공통 Harness 배치와 기존 기능 처리

## 관리 단위

| 위치 | 책임 | 이번 작업 |
| --- | --- | --- |
| tools/agent-harness | 공통 스킬·정책·지원 코드의 한 패키지 | 현재 구현 대상 |
| products/allsen-edge-agent | 제품 요구·소스·기존 검사·향후 Adapter | 기존 검사 유지, 다음 단계에서 연결 |
| infra/deploy | 호스트 준비·배포·승인·관측·복귀 | 이번 공통 패키지에 복제하지 않음 |
| infra/self-hosted-runner | 현재 runner 구현 | ephemeral 전환 실험 이후 deploy로 이관 판단 |
| governance/workspace-rules | 과거 조사·이관 기록 보관 | 정책 스킬 공급 종료, 현재 원본은 agent-harness |

상위 `workspace/AGENTS.md`는 생성하지 않으며 Second Brain은 활성 대상에서 제외

## 공통 패키지 내부

| 경로 | 원본과 소비자 |
| --- | --- |
| skills/ | 기존 개발 스킬과 이관한 정책 스킬의 원본; Skills CLI가 사용자 스킬로 설치 |
| plugins/workflow-core/ | OpenSpec·기존 스킬·명령·검토·인계 연결; Codex plugin으로 설치 |
| plugins/matt-engineering/, plugins/superpowers-execution/ | 선택 upstream의 고정 버전과 조정 사항 |
| src/harnesskit/, schemas/ | 입력 검증·실행·증거·binding·자원 소유권의 결정적 처리 |
| templates/agents/, templates/binding.json | 제품 내부에 설치할 역할 설정과 생성 파일 소유권 |
| .agents/plugins/marketplace.json | 같은 저장소에 있는 plugin의 native 배포 목록 |
| docs/implementation/ | 실제 관측, 이관 판단, 현재 제약 |

제품의 `openspec-*`는 고정 OpenSpec CLI가 생성하며 공통 plugin에 복사하지 않는 구조
공통 스킬과 Harness는 이 저장소의 한 버전으로 관리하며 별도 실행 서비스나 중간 승격 저장소 없음

## 재사용·보완·제외 판단

| 기존 기능 | 판단 | 근거·변경 |
| --- | --- | --- |
| github-operations | 재사용 | 계정·Issue·push·PR·배포 권한의 기존 절차 사용 |
| parallel-worktree-development | 재사용 | native worktree와 agent 분담·로컬 통합 절차 사용 |
| systematic-debugging | 맞춤 구현 유지 | 동일 이름의 upstream을 추가 활성화하지 않는 단일 공급 |
| 문서·README·API·Mermaid·웹 검사 스킬 | 재사용 | 기존 적용 범위 유지; Core에 같은 지침을 다시 작성하지 않음 |
| workspace-governance·development-tooling·github-actions-workflows | 이관 완료 | 같은 패키지의 단일 원본과 설치 경로 사용, 이전 설치용 파일 제거 |
| 별도 governance 저장소 강제 규칙 | 대체 | 사용자가 선택한 공통 Harness 내부의 정책 소유로 변경 |
| Allsen Taskfile·npm 검사 | 재사용 | Adapter가 기존 명령을 호출; 검사 본문 재작성 제외 |
| Matt·Superpowers의 경쟁 planning/worktree/종료 흐름 | 제외 | OpenSpec 정본과 기존 Git·병렬 스킬에 연결 |
| report 검증·후보 fingerprint·binding 충돌·lease | 보완 | 현재 스킬에는 동일한 결정적 실행기가 없어 코드와 실패 테스트 추가 |
| UI logger/viewer 병합 | 선택 사항 | Harness 완료의 필수 조건에서 제외 |

## 정책 공급 전환

2026-09-22 기존 정책 공급을 종료하고 현재 원본을 Agent Harness로 통합
기존 `workspace-rules`의 설치 가능한 스킬 3개·파일 28개를 제거하고 안내 문서를 새 소유자 링크로 전환
공통 정책·범용 절차는 이 패키지, 제품 명세·명령은 제품, 운영 계약·설정은 운영 저장소에서 관리

| 기존 원본 | 현재 소유자·처리 |
| --- | --- |
| `skills/workspace-governance/` | 이 저장소의 같은 경로; category·완료·소유권 규칙 |
| `skills/development-tooling/` | 이 저장소의 같은 경로; 도구 기준·템플릿·렌더러 |
| `skills/github-actions-workflows/` | 이 저장소의 같은 경로; Actions 정책·예제 |
| `docs/codex-skill.md`, `docs/ci-cd-map.md` | 이 저장소의 같은 경로; 기존 문서는 이동 안내 |
| 기존 `docs/research/`, `docs/plans/`, 이관 기록·patch | 이전 저장소의 역사적 기록으로 보존; 현재 정책 공급에서 제외 |
| 제품별 실행 계약 | Allsen 소유 문서·기존 명령; 옛 정책 저장소 참조 없음 확인 |
| 운영 실행 계약 | deploy·runner 소유 문서; runner의 남은 공통 정책 참조 전환 |

전환 전 기준은 [workspace-rules의 마지막 정책 snapshot](https://github.com/suchang-busan/workspace-rules/blob/201cb7bdd43ebce7e40ea89a8c34aed4fe605b2a/README.md), revision `201cb7bdd43ebce7e40ea89a8c34aed4fe605b2a`
28개 파일 모두 수신 경로 존재 확인, 18개는 byte 동일, 10개 차이는 소유권·참조 전환과 앞서 승인된 Harness 실행·검사 경계 반영
Git 이력과 과거 조사 자료를 유지하며 원본 이력을 새 이력으로 합쳤다고 표현하지 않는 방식

### 소비와 설치

Windows 활성 checkout과 사용자 설치본을 검사 대상으로 사용
Allsen·deploy·windshift에서 이전 정책 저장소의 활성 참조 없음 확인, runner의 남은 1개 참조는 Agent Harness로 전환
정책 스킬 3개의 설치 출처는 `tttaliesin/agent-harness`, 설치 내용은 현재 원본과 일치해야 하는 조건
Codex의 실제 발견 목록에서 같은 이름의 스킬이 한 번씩 나오는지 확인
과거 WSL 보존본·linked worktree는 자동 동기화 대상에서 제외하고 이전 commit의 작업 근거로 보존

### 복귀와 후속 경계

전환 이상 시 위 snapshot과 전환 전 Agent Harness `5c46b52921d05f12bad725440c92e55000bc4dc6`을 대조해 필요한 변경만 복귀
정책 공급을 이전 위치로 되돌릴 때는 소비 참조·설치본도 함께 전환하고 같은 이름의 두 공급을 동시에 활성화하지 않는 기준
원격 저장소 archive·삭제, 앱 프로젝트 제거는 정책 공급 종료와 별도 작업
Allsen Adapter와 실제 제품·CI·runner 통합은 다음 단계에서 검증
