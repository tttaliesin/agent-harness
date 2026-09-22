# 실제 환경 조사

관측일: 2026-09-22
`SUPPORTED`는 표에 기재한 관측 범위의 지원을 뜻하며 전체 제품 인수 통과와 구분

| 항목 | 실제 관측 | 상태·범위 |
| --- | --- | --- |
| Codex CLI | 0.155.0-alpha.9.2 | SUPPORTED: app-server schema 생성과 skills/list·hooks/list 응답 |
| Desktop 표시 버전 | 패키지 조회에서 미확인 | UNVERIFIED: CLI 버전을 Desktop 버전으로 대체하지 않음 |
| Native hooks | sessionStart·stop·subagentStop·interrupt enum 확인 | SUPPORTED: schema; 새 plugin의 실제 실행은 별도 신뢰 승인 필요 |
| 기존 사용자 hook | Interrupt, enabled, trusted 조회 | SUPPORTED: 기존 설치 관측이며 새 Core hook 통과 근거는 아님 |
| Plugin manifest | .codex-plugin/plugin.json, hooks/hooks.json | SUPPORTED: 설치된 scaffold/validator와 공식 문서 확인 |
| Native role | .codex/agents/*.toml, read-only 설정 | UNVERIFIED: 선언과 실제 쓰기 제한은 별도 검증 |
| Python | Windows·WSL 3.12.14 | SUPPORTED: 공통 CLI의 선택 interpreter |
| uv | WSL 0.12.10, 작업 전용 Windows 0.12.10 | SUPPORTED: 정확한 버전과 경로 확인 |
| just | 1.58.0 | SUPPORTED: 공식 artifact SHA256 확인, 작업 전용 설치 |
| mise | WSL 2026.8.10 | SUPPORTED: Linux 도구 선택; Windows native mise 미검증 |
| Node | Windows 24.19.0 | SUPPORTED: OpenSpec 조사용 runtime |
| OpenSpec | 1.13.1 | SUPPORTED: pinned CLI; 생성 결과는 openspec-binding.md 참고 |
| Docker Compose | WSL v5.4.0 | SUPPORTED: 버전 조회; fixture 실행은 다음 단계 |
| process-compose | 설치 경로 없음 | UNVERIFIED: 제품 fixture 단계에서 필요한 경우 설치·검증 |
| GitHub 저장소 | tttaliesin/agent-harness public, workspace-rules private | 정책 공급은 agent-harness로 전환; [범위·복귀 기준](layout-map.md#정책-공급-전환) 참조 |

## 관측 방법

- 설치된 Codex의 `app-server generate-json-schema --experimental`로 현재 입력·출력 schema 확인
- 별도 app-server를 초기화하여 `skills/list`와 `hooks/list` 호출; 새 task·모델 실행·내부 DB 수정 없음
- 공식 OpenSpec 1.13.1을 작업 전용 경로에 설치하여 실제 help·생성 경로 확인
- just 1.58.0의 Windows·Linux 공식 release artifact와 SHA256 대조
- GitHub repo 조회에서 public visibility와 ADMIN 권한 재확인; 기존 visibility 유지
- 사용자 요청에 따라 최종 추적 파일과 미전송 커밋 이력을 Gitleaks 및 주소·개인정보 후보 검사로 검토한 뒤 push; 성공 여부는 원격 main SHA와 별도 전달 기록으로 확인

## 공식 근거

- [Codex hooks](https://learn.chatgpt.com/docs/hooks): plugin hook도 현재 정의의 신뢰 검토 필요
- [Codex subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): standalone role 설정과 상속 권한
- [OpenSpec CLI](https://github.com/Fission-AI/OpenSpec/blob/v1.13.1/docs/cli.md): 실제 설치 버전 help와 함께 대조
- [just 1.58.0](https://github.com/casey/just/releases/tag/1.58.0): 도구 artifact 출처

원문 루트 `plugin.json` 예시는 현재 loader에 맞춰 `.codex-plugin/plugin.json`으로 배치
상위 작업공간 지시 파일이나 별도 플랫폼 저장소를 추가할 필요는 없음
