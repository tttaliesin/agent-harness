# 공통 Harness 배치와 기존 기능 처리

## 관리 단위

| 위치 | 책임 | 이번 작업 |
| --- | --- | --- |
| tools/developer-skills | 공통 스킬·정책·지원 코드의 한 패키지 | 현재 구현 대상 |
| products/allsen-edge-agent | 제품 요구·소스·기존 검사·향후 Adapter | 기존 검사 유지, 다음 단계에서 연결 |
| infra/deploy | 호스트 준비·배포·승인·관측·복귀 | 이번 공통 패키지에 복제하지 않음 |
| infra/self-hosted-runner | 현재 runner 구현 | ephemeral 전환 실험 이후 deploy로 이관 판단 |
| governance/workspace-rules | 기존 공통 정책 공급 | 세 스킬 이관 검증 후 기존 공급 종료 |

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
| workspace-governance·development-tooling·github-actions-workflows | 이관 | 같은 패키지의 원본으로 합치고 참조 전환 |
| 별도 governance 저장소 강제 규칙 | 대체 | 사용자가 선택한 공통 Harness 내부의 정책 소유로 변경 |
| Allsen Taskfile·npm 검사 | 재사용 | Adapter가 기존 명령을 호출; 검사 본문 재작성 제외 |
| Matt·Superpowers의 경쟁 planning/worktree/종료 흐름 | 제외 | OpenSpec 정본과 기존 Git·병렬 스킬에 연결 |
| report 검증·후보 fingerprint·binding 충돌·lease | 보완 | 현재 스킬에는 동일한 결정적 실행기가 없어 코드와 실패 테스트 추가 |
| UI logger/viewer 병합 | 선택 사항 | Harness 완료의 필수 조건에서 제외 |

## 원본 공급 전환 조건

1. 이관한 세 스킬의 참조·내용 검사와 새 경로 설치 확인
2. 모든 활성 공급에서 같은 이름이 한 번만 발견되는지 확인
3. 이전 공급 경로를 사용하는 저장소 안내·설치 lock 전환
4. 새 저장소의 공개 범위 확정과 단위별 원격 반영
5. 기존 공급 종료 안내와 복귀할 revision 보존

원본 저장소 삭제나 기존 Git 이력 병합은 이관의 필수 조건이 아님
2026-09-22 확인한 원본 workspace-rules는 private이고 대상 developer-skills는 public이므로 공개 범위 결정 전에는 원격 이관 보류
