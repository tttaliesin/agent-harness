# OpenSpec 생성 경로

## 버전과 profile

버전·npm integrity·선택 workflow의 정본은 [openspec-profile.json](../openspec-profile.json)
2026-09-22 실제 생성에 사용한 OpenSpec 1.13.1과 Node 24.19.0

| 역할 | 실제 생성 이름 |
| --- | --- |
| 탐색 | openspec-explore |
| 제안 | openspec-propose |
| 구현 | openspec-apply-change |
| 변경 갱신 | openspec-update-change |
| 검증 | openspec-verify-change |
| 명세 동기화 | openspec-sync-specs |
| 보관 | openspec-archive-change |

실제 생성 위치는 제품 `.agents/skills/openspec-*/SKILL.md`
`openspec/config.yaml`의 schema는 `spec-driven`이며 요구사항·변경·tasks 정본은 제품 `openspec/`
Codex용 custom prompt는 생성하지 않으며 공통 plugin에도 같은 스킬을 포장하지 않는 구조

## 생성

선택한 Node에서 package manager로 정확한 OpenSpec 버전과 lock을 먼저 설치
생성 명령은 네트워크 설치를 수행하지 않으며 이미 설치된 `bin/openspec.js`와 Node의 절대 경로를 사용

```bash
python scripts/init-openspec.py \
  --product /absolute/product \
  --node /absolute/node \
  --cli /absolute/node_modules/@fission-ai/openspec/bin/openspec.js
```

스크립트가 임시 XDG 설정 경로에 선택 profile을 만들고 공식 `init --tools codex --profile custom`을 호출
사용자 전역 OpenSpec profile을 변경하지 않으며 기존 제품 파일의 처리는 공식 CLI에 맡기는 방식
`--force`로 사용자 문서를 강제 정리하지 않음
완료 후 7개 이름과 실제 생성 경로가 고정 목록과 일치하는지 검사

2026-09-22 격리된 시험 제품에서 위 7개 스킬 생성과 `spec-driven` 설정 확인
실제 Allsen 연결과 제품 변경의 propose→apply→verify→archive 시나리오는 다음 제품 단계의 검증 대상
