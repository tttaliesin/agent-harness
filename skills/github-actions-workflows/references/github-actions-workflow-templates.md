# GitHub Actions workflow templates

독립 모듈 발행과 moving-channel 갱신을 위한 비실행 구조 예제
실제 workflow 작성 전 대상 Product 저장소의 발행 계약과 명령 확인
Action pin, runner label, module planner·publisher 명령과 credential binding은 해당 저장소의 검토된 값을 사용한다.
아래 placeholder를 실제 근거 없이 채우거나 그대로 실행하지 않는다.

## Product CI workflow template

이 예제의 planner는 변경된 module 배열을 matrix 입력으로 제공하며 변경 탐지 기준은 대상 Product의 계약 사용
PR 검증은 publication credential 없는 별도 workflow다.

```yaml
name: Independent module publication
on:
  push:
    branches: [main]
permissions:
  contents: read
jobs:
  plan:
    runs-on: <EVIDENCED_PLANNER_RUNNER>
    outputs:
      modules: ${{ steps.plan.outputs.modules }}
    steps:
      - uses: actions/checkout@<REVIEWED_CHECKOUT_SHA>
        with:
          ref: ${{ github.sha }}
          fetch-depth: 0
          persist-credentials: false
      - id: plan
        run: <PRODUCT_CHANGED_MODULE_PLANNER>
  publish:
    needs: plan
    strategy:
      fail-fast: false
      matrix:
        module: ${{ fromJSON(needs.plan.outputs.modules) }}
    name: Publish image (${{ matrix.module }})
    runs-on: <EVIDENCED_PRODUCT_SHR>
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@<REVIEWED_CHECKOUT_SHA>
        with:
          ref: ${{ github.sha }}
          persist-credentials: false
      - name: Publish one immutable image and update its test channel
        env:
          MODULE: ${{ matrix.module }}
          GHCR_TOKEN: ${{ github.token }}
        run: <PRODUCT_VERIFIED_MODULE_PUBLICATION_COMMAND>
```

## Product command boundaries

`<PRODUCT_CHANGED_MODULE_PLANNER>`는 대상 Product의 변경 탐지 기준으로 module 배열을 `modules` output에 제공하는 저장소 명령
이력 조회 실패를 unchanged로 숨기지 않으며 빈 matrix와 concurrency 처리는 실제 Product workflow에 맞춘다.
`<PRODUCT_VERIFIED_MODULE_PUBLICATION_COMMAND>`는 선택된 모듈만 source 검증·job-local isolated build·immutable identity와 digest 발행·pull-back·label·provenance·해당 smoke 검증 수행
자동 테스트 moving channel은 같은 검증된 manifest에 연결하고 Product-owned 발행 identity로 순서를 확인해 역행과 같은 identity의 다른 digest 거부
Registry credential은 job-local 임시 설정으로 제한하고 실패 시에도 제거한다.
Host Docker socket 사용 금지, 실패한 검증 뒤 moving channel 갱신 금지
Tag·digest·metadata·artifact 관계와 중복 publish 처리는 Product 계약 준수

발행 알림이 필요한 경우 [소비자 연결 계약](github-actions-workflows.md#소비자-연결)과 실제 수신 interface에 맞춰 별도 단계 구성
이 예제의 job·tag·artifact 형태를 다른 Product에 강제하지 않는 원칙
