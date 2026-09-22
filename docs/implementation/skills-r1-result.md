# R1 공통 스킬 저장소 정리 결과

기준일: 2026-09-22
구현 기준: `0e7e74ea734e0119935fa39b258f2d0cb05b16e1`

## 반영 내용

- 공통 스킬 28개에서 독립 항목 9개를 통합·종료하고 19개를 root skills로 공급
- 자체 실행 CLI·전용 schema·binding·역할 template·hook과 플러그인 3개의 중복 공급 제거
- 제품 명령 직접 사용으로 정책 수정, npx skills를 README 첫 설치 경로로 배치
- 선택 설치에 필요한 참고 자료·license 포함, upstream Git object·원본·patch 검증 유지
- 제품용 Python package·wheel build 제거, Python·uv·just는 유지보수 검사에 한정

## 확인한 결과

| 검사 | 관측 결과 |
| --- | --- |
| 유지보수 check | Ruff 통과, 테스트 33개·하위 사례 12개 통과 |
| 스킬 형식 | 공식 skill-creator 검사에서 19개 통과; Windows UTF-8 모드 사용 |
| 참조·출처 | 원본·변경 patch·license·필수 Markdown 참조 검사 통과 |
| 실제 설치 도구 | Skills CLI 1.5.26에서 19개 발견 |
| 선택 설치 | code-review와 test-driven-development를 서로 다른 시험 폴더에 단독 설치 |
| 설치 파일 | 각각 5개·3개 파일이 원본과 일치 |
| 독립 검토 | 명세·Standards 검토에서 추가 조치가 필요한 지적 0건 |
| 공개 전 민감정보 | 구현 commit 신규 탐지 0건; 전체 tree의 3건은 실제 artifact SHA256과 일치 |

Git diff 공백 검사는 실제 소스·문서에서 통과
provenance patch의 빈 context 행은 unified diff 형식에 필요한 한 칸 공백으로 보존하고, 원본 대비 patch 내용 검사로 확인
독립 검토자는 참조·출처 검사를 확인했으며 전체 테스트와 설치 시험은 주 작업의 실행 근거를 사용
원격 CI 결과는 [저장소 검사 workflow](https://github.com/tttaliesin/agent-harness/actions/workflows/check.yml)의 실제 commit과 대조

## 소비자와 남은 범위

Windows 활성 Allsen·deploy·runner 파일 검색에서 제거한 CLI·Adapter 호출 미발견
현재 Codex 사용자 설정에는 기존 플러그인 3개가 남아 있으며 이 작업에서 설치본·설정 변경 미수행
이전 checkout의 ignored 환경·build 결과도 사용자 상태로 보존

다음 단계는 [설치 전환](../skills-migration.md)의 R2
실제 사용자 설치·갱신·복구, 두 제품 예제의 사용과 Allsen·운영 환경 검증은 별도 미완료
단독 설치 시험을 두 제품 fixture의 H07 검증이나 실제 Codex 작업 완료로 집계하는 방식 제외
