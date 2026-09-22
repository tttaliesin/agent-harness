# 스킬 공급과 기존 프로젝트의 책임

## 원본과 소비

| 위치 | 책임 |
| --- | --- |
| agent-harness/skills | 공통 개발·정책 스킬과 구체적인 보조 도구 |
| agent-harness/provenance | 선택 upstream 원본·license·Git object·적용 patch |
| agent-harness/scripts·tests | 저장소 유지보수 검사 |
| 사용자 또는 제품의 .agents/skills | 선택 설치한 스킬; 같은 이름의 중복 공급 방지 |
| 제품 저장소 | 요구·소스·명령·검사·제품별 지침 |
| infra/deploy·runner | 실제 CI 인프라·배포·관측·복구 |
| workspace-rules | 정책 공급을 종료한 역사 자료 |

Codex가 스킬을 읽고 제품의 기존 명령 실행
npx skills는 설치·갱신 도구이며 공통 실행 서비스·제품 Adapter 요구 없음
제품의 Taskfile·npm·Go·Python 검사 본문 유지
원문 구축 대상에는 OpenSpec 7개와 제품 명세 흐름 연결 필요; 현재 실제 연결 미완료
Web·Python·Streaming 기능과 두 실행 예제도 미완료 상태로 유지
상세 책임과 완료 조건은 [원문 요구 대조](requirements-coverage.md) 참조
제품 명세를 기준으로 삼고 별도 change YAML 추가 제외

## 기존 구성 정리

상위 workspace/AGENTS.md 재생성 제외, SecondBrain은 활성 대상에서 제외
Allsen Adapter 생성 계획 철회, 스킬 설치를 위한 제품 도구 전환 제외
runner의 deploy/runners 통합 방향은 독립 인프라 작업에서 소비자·복구 검증 후 진행

현재 설치 전환 상태는 [전환 안내](../skills-migration.md), 유지보수 방법은 [검사 안내](../maintenance.md) 참조
