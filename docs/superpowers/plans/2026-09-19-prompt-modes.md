# Prompt Modes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 맞춤법 기본 검사와 선택형 날짜·순화어·문체 검사를 분리하고 AI 응답을 엄격히 검증한다.

**Architecture:** `rag_context.py`는 선택된 지침 절만 반환하고 `ai_client.py`는 옵션별 프롬프트와 허용 오류 유형을 구성한다. `app.py`는 기본 해제 체크박스 세 개의 상태를 작업 스레드에 전달한다.

**Tech Stack:** Python 3, PyQt6, unittest, requests

---

### Task 1: 프롬프트 모드 테스트

**Files:**
- Modify: `tests/test_ai_client.py`
- Create: `tests/test_rag_context.py`

- [ ] 기본 프롬프트에서 선택 지침이 제외되는 테스트를 작성한다.
- [ ] 세 옵션이 대응하는 지침만 포함하는 테스트를 작성한다.
- [ ] 테스트를 실행해 새 API가 없어서 실패하는 것을 확인한다.
- [ ] `rag_context.py`의 절 선택과 `ai_client.py`의 옵션별 프롬프트를 구현한다.
- [ ] 관련 테스트가 통과하는지 확인한다.

### Task 2: 응답 검증 테스트

**Files:**
- Modify: `tests/test_ai_client.py`
- Modify: `src/ai_client.py`

- [ ] 정상, 빈 배열, 잘못된 JSON, 필드 누락, 허위 원문, 잘못된 유형, 중복 응답 테스트를 작성한다.
- [ ] 기존 구현에서 실패하는지 확인한다.
- [ ] `InvalidAIResponseError`와 문서 기반 검증을 구현한다.
- [ ] 잘못된 응답이 배치 fallback으로 전달되는지 확인한다.

### Task 3: UI 체크박스와 작업 전달

**Files:**
- Modify: `src/app.py`
- Create: `tests/test_app_options.py`

- [ ] 체크박스 세 개가 기본 해제되는 UI 테스트를 작성한다.
- [ ] `MainWindow.get_review_options()` 결과와 처리 중 활성 상태를 테스트한다.
- [ ] 체크박스와 `CheckWorker` 옵션 전달을 구현한다.
- [ ] UI 테스트가 통과하는지 확인한다.

### Task 4: 전체 검증과 Claude 리뷰

**Files:**
- Modify: Claude 리뷰에서 확인된 결함이 있는 파일

- [ ] `python -m unittest discover -s tests -v`를 실행한다.
- [ ] 모든 Python 파일을 AST로 파싱한다.
- [ ] Claude CLI를 도구 없는 review 모드로 실행한다.
- [ ] 유효한 지적을 수정하고 관련 회귀 테스트를 추가한다.
- [ ] 전체 테스트와 diff 검사를 다시 실행한다.
