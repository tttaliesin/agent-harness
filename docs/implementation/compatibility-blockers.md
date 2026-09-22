# 남은 연결·검증 조건

| 항목 | 상태와 영향 | 해소·재검증 |
| --- | --- | --- |
| Private 정책을 public 대상으로 이관 | BLOCKED: 원격 반영과 이전 공급 종료 | 사용자가 통합 결과의 공개 범위 결정 후 실제 target visibility 재조회 |
| Native hook trust | NOT_CONFIGURED: 설치만으로 hook 실행되지 않음 | 현재 정의를 Codex에서 검토·trust하고 SessionStart·Stop·SubagentStop·Interrupt 실험 |
| Native read-only enforcement | UNVERIFIED: 역할 파일만으로 공식 리뷰 완료 불가 | 새 제품 task에서 쓰기 거부·명령 권한·전후 tree 관측 |
| 실제 CI provenance | BLOCKED: JSON·환경변수로 공식 evidence 승인 금지 | 제품 CI 단계에서 immutable run/attempt/head/artifact를 검증하는 provider 연결 |
| Host resource probe | BLOCKED: 자원이 명시된 검사는 가짜 검사로 통과 불가 | 제품 fixture 단계에서 실제 포트·장치·서비스 준비 상태 검사 연결 |
| Web/Python/Streaming Pack과 두 fixture | NOT_STARTED: 실제 제품 기능 인수는 남아 있음 | 다음 단계에서 Allsen 명령 Adapter와 두 fixture 실행 |
| Ephemeral runner·Komodo 승인/관측/복귀 | NOT_STARTED: 공통 CLI 구현과 별도 운영 연결 | 기존 runner·deploy 근거로 다음 CI/배포 단계 수행 |

개별 함수·unit test·manifest 로딩은 관련 부분의 증거이며 H01–H26 전체 PASS로 확대하지 않는 기준
차단된 기능을 항상 PASS하는 대체 경로나 내부 DB 변경으로 우회하지 않는 구현
