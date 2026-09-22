# `platforms/` 운영 규칙

이 문서는 `platforms/`에 두는 application platform의 이상적인 역할을 정한다.

## 여러 product가 쓰는 application capability를 둔다

`platforms/`에는 여러 product가 application 수준에서 소비하는 service와 capability를 둔다.
platform은 product가 source를 복사하지 않고 interface를 통해 사용할 수 있는 공통 기능을
제공한다.

## 소비할 interface를 분명히 한다

platform은 product가 사용할 interface와 호환되는 변경 방법을 함께 제공한다. product는 그
interface를 소비하고, platform 내부 구현이나 runtime 설정을 직접 소유하지 않는다.

## product와 infra 사이를 구분한다

특정 사용자·고객에게 제공하는 기능과 경험은 `products/`에 둔다. runtime, 배포, release와 같은
실행 기반은 `infra/`에 둔다. AI 학습, simulator, 분석의 근거로 보존할 원천 자료는 `data/`에 둔다.
