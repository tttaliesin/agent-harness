# 저장소 유지보수

이 문서의 Python·uv·just 환경은 스킬 원본과 보조 도구를 검사하는 기여자용 환경
일반 사용자의 설치는 [README](../README.md)에서 시작

## 환경과 검사

저장소 루트에서 mise.toml·mise.lock의 검토된 Python·uv·just 선택
의존성 설치와 검사를 분리하여 실행

```sh
just doctor
just sync
just check
```

doctor는 선택한 Python·uv 확인, sync는 커밋된 lock에 따른 명시적 설치
check는 Ruff·스킬 및 출처 검사·실패 사례 테스트 실행
결과 보고서는 .reports/pytest.xml에 생성, 제품용 wheel·CLI build 없음

스킬의 script를 변경할 때 해당 스킬의 관련 검사도 실행
정적 스킬 검증과 실제 Codex 호출·제품 시나리오 검증은 별도로 기록

## 출처와 lock 변경

upstream.lock.json은 이 저장소 유지보수 자료로만 사용
소비 제품에 복사하거나 별도 lock을 생성하는 계약 없음
검사 도구는 네트워크 없이 원본 Git object·SHA·license·변경 patch와 현재 파일을 대조
Git object 증명은 저장한 commit과 원본 파일의 관계를 확인하며 원격 출처의 신뢰성을 독립적으로 증명하지 않는 범위

1. upstream 저장소·정확한 commit·license를 확인하고 선별 범위 결정
2. 변경한 원본·적용 결과·patch와 출처 기록을 함께 검토
3. 스킬의 실제 작업 예제와 필요한 보조 도구 회귀 확인
4. 검토된 source 기록을 유지한 상태에서 artifact 목록 갱신

```sh
uv run --no-sync python scripts/refresh-package-lock.py
uv run --no-sync python scripts/refresh-package-lock.py --write
just check
```

refresh는 source pin·license·적용 결과를 자동 승인하는 updater가 아니며 출처 불일치 시 실패
일반 검사는 lock 갱신·설치·원격 변경 미수행
실제 배포 가능한 스킬에는 선택 설치 후에도 필요한 license와 참조가 포함되는지 확인
