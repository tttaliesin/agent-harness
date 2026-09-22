# `data/` 운영 규칙

이 문서는 `data/`에 두는 원천 자료 repository의 이상적인 역할을 정한다.

## 재사용할 원천 자료를 보존한다

`data/`에는 AI 학습, simulator, 분석처럼 여러 작업의 근거로 재사용할 원천 자료를 둔다.
repository는 자료 자체와 자료의 출처·용도·사용 조건을 함께 보존해, 소비자가 어떤 자료를
근거로 삼는지 알 수 한다.

원천 자료는 가능한 한 원래 형태와 구분해 보존한다. 자료를 가공하거나 생성해 얻은 결과로
원천 자료를 덮어쓰지 않는다.

## 소비 작업은 다른 category에 둔다

AI 학습을 실행하는 code와 학습 결과 model은 그 결과를 제공하는 category에 둔다. simulator의
source와 실행 구성도 simulator가 제공하는 결과의 category에 둔다. 분석 방법과 결론은
`research/`에 둔다.

이 작업들은 `data/`의 원천 자료를 특정 version으로 참조할 수 있지만, 원천 자료 repository가
학습·simulator·분석 구현을 소유하지 않는다.

## 자료와 구현의 경계를 지킨다

사용자·고객에게 제공하는 기능은 `products/`에 둔다. 여러 product가 interface로 사용하는
application capability는 `platforms/`에 둔다. runtime과 배포 기반은 `infra/`에 둔다.
