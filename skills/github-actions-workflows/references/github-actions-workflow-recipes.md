# GitHub Actions workflow 구현 recipe

[Product CI 정책](github-actions-workflows.md)을 실제 workflow에 적용할 때 사용할 검증 사례
새 workflow 구조가 필요한 경우에만 [발행 예제](github-actions-workflow-templates.md) 참고

## Product 발행 검증

| 상황 | 확인할 결과 |
| --- | --- |
| 모듈 또는 공유 build input 변경 | 현재 catalog와 의존 관계에 맞는 build 대상 선택 |
| 이전 검증 발행 부재·조회 실패 | 근거 없는 unchanged 판정 방지 |
| 일부 모듈 실패 | 성공한 sibling의 발행·channel 갱신 유지 |
| 동일 발행 identity 재실행 | 같은 digest의 중복 처리와 다른 digest의 충돌 구분 |
| 오래된 실행 재시도·동시 발행 | Moving channel의 이전 발행 역행 방지 |
| Registry 인증·transport 실패 | Tag 부재나 발행 성공으로 오판하지 않는 결과 |
| Channel 갱신 이후 | 같은 manifest·source·module provenance의 pull-back 확인 |

변경한 동작과 관련된 사례만 실제 저장소의 검사 도구로 확인
Planner·publisher·metadata 형식은 해당 Product의 계약과 구현에서 확인

## 소비자와 실행 기반 확인

설치 릴리스 변경 시 기존 digest 재사용·Compose 커밋 일치·실제 설치 검사와 upgrade 지원 범위 확인
실행 기반 변경 시 소비 workflow에 필요한 도구·repository scope·접근 범위를 해당 runner의 계약과 대조
일반 workflow 보안은 [스킬의 보안 규칙](../SKILL.md#generic-workflow-and-security-rules) 적용
배포·서버 준비·러너 등록·서비스 복구의 검증은 해당 소유 저장소에서 수행하며 이 recipe에 별도 운영 checklist 유지 금지
