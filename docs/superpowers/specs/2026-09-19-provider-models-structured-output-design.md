# AI 공급자 모델 및 구조화 출력 개선 설계

## 목적

오타 검사에 사용하는 기본 모델을 최신 안정 모델로 조정하고, 모델 교체가 필요할 때 코드 수정 없이 환경변수로 재정의할 수 있게 한다. 세 공급자 모두 동일한 오류 JSON Schema를 사용해 형식 오류와 불필요한 재시도를 줄인다.

## 기본 모델

- Gemini: `gemini-3.8-flash`
- OpenAI: `gpt-5.6-terra`
- Anthropic: `claude-haiku-4-5-20251001`

애플리케이션은 API 키 접두사로 공급자를 감지하고 해당 공급자의 기본 모델 하나만 사용한다. 공급자 간 자동 전환은 하지 않는다.

## 모델 설정

기본 모델은 코드의 공급자별 모델 맵에 둔다. 다음 환경변수가 설정되어 있으면 해당 값이 기본 모델보다 우선한다.

- `TYPO_GEMINI_MODEL`
- `TYPO_OPENAI_MODEL`
- `TYPO_ANTHROPIC_MODEL`

빈 환경변수는 무시하고 기본 모델을 사용한다. `latest` 별칭은 기본값으로 사용하지 않아 모델 동작이 예고 없이 바뀌는 것을 피한다.

## API 키 입력 안내

API 키 입력 대화상자에 지원 공급자와 실제 기본 모델을 함께 표시한다.

- Gemini — `gemini-3.8-flash`
- OpenAI — `gpt-5.6-terra`
- Anthropic — `claude-haiku-4-5-20251001`

키 저장 완료 메시지에는 감지한 공급자와 실제 선택된 모델을 표시한다. 환경변수로 모델이 재정의된 경우 완료 메시지에도 재정의된 모델명이 나타나야 한다.

## 공통 JSON Schema

오류 응답 스키마는 `ai_client.py` 한 곳에서 생성한다. 스키마는 현재 활성화된 검사 옵션에 따라 허용되는 `errorType` 열거형을 동적으로 구성한다.

최상위 객체는 `errors` 배열만 허용한다. 각 오류 객체는 다음 필드를 모두 요구하며 추가 필드는 허용하지 않는다.

- `page`: 정수
- `sentence`: 문자열
- `original`: 문자열
- `corrected`: 문자열
- `reason`: 문자열
- `errorType`: 활성 검사 모드에 맞는 열거형 문자열

구조화 출력은 JSON 문법과 필드 형식을 보장하는 역할만 한다. 입력 문장 일치, 원문 포함 여부, 허용 오류 유형, 중복 제거 등 기존 의미 검증은 계속 수행한다.

## 공급자별 요청

### Gemini

기존 `generateContent` 호출을 유지한다. `generationConfig`에 `responseMimeType: application/json`과 JSON Schema를 함께 전달한다. 모델은 `gemini-3.8-flash`를 기본으로 사용한다.

### OpenAI

기존 Chat Completions 호출을 유지한다. 단순 `json_object` 대신 `json_schema`와 `strict: true`를 사용한다. 모델은 `gpt-5.6-terra`를 기본으로 사용한다.

### Anthropic

기존 Messages API 호출을 유지한다. `output_config.format`에 JSON Schema를 전달한다. 모델은 Haiku 4.5를 유지하되 환경변수로 교체 가능하게 한다.

## 오류 처리와 호환성

- API가 구조화 출력 요청을 거부하면 해당 배치는 실패로 처리하고 기존 순차 재시도 경로를 따른다.
- 스키마 없는 요청으로 자동 강등하지 않는다. 자동 강등은 공급자별 결과 형식을 다르게 만들어 오류를 숨길 수 있기 때문이다.
- 최종 재시도까지 실패하면 기존 `BatchProcessingError`를 사용자에게 표시한다.
- 공급자 API 응답이 비어 있거나 스키마 이후에도 의미 검증을 통과하지 못하면 성공으로 처리하지 않는다.

## 테스트

테스트는 구현보다 먼저 추가한다.

1. 기본 모델 세 개가 확정 값과 일치하는지 검사한다.
2. 공급자별 환경변수가 모델명을 재정의하는지 검사한다.
3. 선택 검사 모드에 따라 JSON Schema의 `errorType` 열거형이 달라지는지 검사한다.
4. Gemini 요청에 JSON Schema가 포함되는지 검사한다.
5. OpenAI 요청이 `json_schema`와 `strict: true`를 사용하는지 검사한다.
6. Anthropic 요청에 `output_config.format` 스키마가 포함되는지 검사한다.
7. API 키 입력 안내와 완료 메시지에서 모델명이 표시되는지 검사한다.
8. 기존 프롬프트, 응답 검증, fallback 및 UI 기본값 테스트를 모두 다시 실행한다.

## 제외 범위

- 모델 선택 드롭다운 추가
- 공급자 간 자동 fallback
- `latest` 모델 별칭 사용
- 실제 API를 호출하는 유료 통합 테스트
- 모델별 한국어 오타 정확도 벤치마크 자동화
