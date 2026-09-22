# 스킬 관리

공통 정책은 이 저장소에서, 특정 시스템의 실행 지침은 그 구현 저장소에서 관리한다.
스킬 형식 자체가 소유권을 결정하지 않는다.

## 정본과 설치 위치

| 스킬 또는 도구 | 정본 소유자 | 소유 저장소 안의 경로 |
| --- | --- | --- |
| 개발 toolchain·공통 task·전환 템플릿 | 이 저장소 | `skills/development-tooling` |
| Workspace governance | 이 저장소 | `skills/workspace-governance` |
| Markdown authoring | [Developer Skills](https://github.com/tttaliesin/developer-skills) | `skills/markdown-authoring` |
| GitHub operations | [Developer Skills](https://github.com/tttaliesin/developer-skills) | `skills/github-operations` |
| Generic Actions·Product CI 정책 | 이 저장소 | `skills/github-actions-workflows` |
| Deployment promotion | [Deploy](https://github.com/suchang-busan/deploy) | `skills/deployment-promotion` |
| Persistent runner management | [Self-hosted runner](https://github.com/suchang-busan/self-hosted-runner) | `skills/self-hosted-runner-management` |
| Target host management | [Deploy](https://github.com/suchang-busan/deploy) | `skills/target-host-management` |
| Parallel worktree development | [Developer Skills](https://github.com/tttaliesin/developer-skills) | `skills/parallel-worktree-development` |

각 저장소의 README와 package 검증 절차를 먼저 확인한다.
필요한 운영 스킬이 설치되어 있지 않으면 대상 저장소의 문서에서 접근 가능한 계약을 확인하고, 영향받는 작업의 미확인 경계만 보고한다.
Sibling 스킬이 같은 디렉터리에 설치됐다고 가정하지 않는다.
Developer Skills Git 정본: [Developer Skills](https://github.com/tttaliesin/developer-skills)

## 정본 수정

규칙 본문은 `skills/<SKILL_NAME>/references/`에서 직접 관리한다.
`SKILL.md`는 해당 규칙으로 연결하고, README는 사람이 필요한 문서를 찾는 진입점으로 사용한다.
`docs/`에는 저장소 관리 안내와 조사·계획 기록을 둔다.
정책 본문을 복제하지 않고 변경 이력은 Git으로 관리
공통 Harness의 upstream lock·artifact hash·실행 evidence는 패키지 무결성과 검증 입력의 기록이며 정책 문서의 두 번째 원본이 아님

공통 규칙은 달성할 목적과 유지할 안전·소유권 경계를 먼저 명시
현재 소유 저장소의 파일 경로, schema, workflow, PR 방식, 재시도 방법과 도구는 목적에 꼭 필요한 경우에만 공통 강제로 승격
소비 문서는 필요한 interface와 소유 문서로 연결하고 제공자의 내부 절차·지원 범위·현재 상태를 재정의하지 않는 원칙
구현 경로·수량·운영 상태는 해당 저장소에서 조회하고, 과거 구현의 폐지 경위는 기존 변경 기록에서 확인

각 스킬의 실행 도구는 그 스킬의 `scripts/`에 둔다.
여러 Core 연결 스킬이 사용하는 공통 실행·증거 처리는 같은 패키지의 `src/harnesskit/`에서 공유하며 스킬마다 복제하지 않는다.
도구를 수정할 때 변경한 동작과 관련 실패 조건을 확인하고 결과를 보고한다.
Harness 실행·검증 코드에는 요청된 단위·통합·실패 사례 검사를 유지하며, 단순 문서 복사를 위한 별도 테스트 체계는 추가하지 않는 기준

## 승인 범위와 설치본 일치

Skill 전환은 같은 작업 안의 routing이며 기존 승인을 유지한다.
같은 승인 범위는 대상·행위·환경·외부 효과와 명시된 유효 조건으로 판단한다.
단계나 스킬 전환만으로 승인이 만료되지는 않으며, 조건이 달라지면 영향받는 행위만 다시 확인한다.
일회성·매 실행 승인과 명시적인 만료 조건은 그대로 유지한다.
명시적 승인, 운영 target 검증과 credential 경계는 해당 변경 직전에 적용하고, 그 전에 가능한 독립 작업을 완료한다.
검토는 발견 사항·증거·한계 보고, 로컬 구현은 요청된 변경·관련 검증, 외부 실행은 실제 결과 확인으로 완료한다.
Readiness 확인은 해당 operation의 실행 전제조건 확인이며 승인되지 않은 mutation이나 전체 canary 실행을 요구하지 않는다.
이미 승인된 후속 단계가 남았으면 단계 전환만을 이유로 최종 응답을 보내고 재지시를 기다리지 않는다.
실제 실행하지 않은 canary를 성공으로 보고하지 않는다.

설치 전에 정본과 설치본의 차이를 확인한다.
승인된 설치본 전용 변경은 정본에 반영한 뒤 설치본을 갱신한다.
설치 갱신이 승인된 작업은 변경된 파일의 내용이 설치본에 반영됐는지 확인한다.
저장소만 변경한 작업은 설치본 갱신 여부를 별도로 보고하며 commit·push를 설치 승인으로 해석하지 않는다.

## 외부 스킬 개인 수정 기록

외부 스킬의 승인된 수정과 upstream 대응은 [Developer Skills](https://github.com/tttaliesin/developer-skills)가 소유
현재 유지보수 의도는 [개인 수정 기록](local-skill-customizations.md)에서 확인
이전 [이관 기록](https://github.com/suchang-busan/workspace-rules/blob/c8c4e6f9547e0ec9c82e9c4445be9502d48b4f6d/docs/ownership-migration.md)과 [기존 patch](https://github.com/suchang-busan/workspace-rules/blob/c8c4e6f9547e0ec9c82e9c4445be9502d48b4f6d/docs/agent-autonomy-local.patch)는 이전 저장소의 고정 commit에서 확인하는 역사적 증거
새 수정이나 활성 plugin version은 이 파일에 누적하지 않는다.
Upstream 갱신 시 새 소유자의 승인 기록과 현재 원문을 대조하고 검토 없이 과거 patch를 자동 적용하지 않는다.
System/plugin 관리 패키지의 설치 소유권은 유지한다.

## 설치와 갱신

소유 저장소 root에서 필요한 package를 선택해 Skills CLI로 설치한다.
아래 예시는 이 저장소의 정책 스킬이며 운영 스킬은 위 표의 소유 저장소에서 같은 절차를 따른다.

```bash
npx skills add ./skills/workspace-governance --agent codex --global --yes
```

Local directory 설치본은 source 변경만으로 갱신되지 않으므로 설치 승인이 있는 경우 같은 add 명령으로 갱신한 뒤 변경된 파일의 내용을 확인한다.
이관 검증의 임시 package 복사와 실제 agent profile 설치를 구분한다.
