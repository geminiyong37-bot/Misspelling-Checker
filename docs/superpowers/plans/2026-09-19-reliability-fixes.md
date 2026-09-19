# Reliability Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** CLI, kordoc 연동, Python 의존성, AI 배치 실패 처리, 저장소 위생 문제를 수정한다.

**Architecture:** 기존 GUI 흐름은 유지한다. 문서 파서에는 하나의 경로 결정 함수를 두고, AI 검사기는 병렬 1차 시도 후 실패 배치만 순차 fallback하며 최종 실패를 예외로 전달한다.

**Tech Stack:** Python 3, unittest, PyQt6, requests, PyInstaller, Node.js/kordoc

---

### Task 1: 회귀 테스트 작성

**Files:**
- Create: `tests/test_cli.py`
- Create: `tests/test_hwp_parser.py`
- Create: `tests/test_ai_client.py`

- [ ] CLI `--help`, kordoc 경로 결정, AI fallback 성공 및 최종 실패 테스트를 먼저 작성한다.
- [ ] `python -m unittest discover -s tests -v`를 실행해 현재 코드에서 의도한 이유로 실패하는지 확인한다.

### Task 2: CLI와 kordoc 연동 수정

**Files:**
- Modify: `src/main.py`
- Modify: `src/hwp_parser.py`
- Modify: `build.spec`

- [ ] CLI가 `run_ai_check`를 가져오고 호출하도록 변경한다.
- [ ] 개발 기본 경로, `KORDOC_HOME`, PyInstaller 번들 경로가 모두 `cli.cjs`를 사용하도록 구현한다.
- [ ] `build.spec`의 데이터 원본을 `../Archive/kordoc`으로 변경한다.
- [ ] 관련 테스트를 실행해 통과를 확인한다.

### Task 3: AI fallback 구현

**Files:**
- Modify: `src/ai_client.py`

- [ ] 병렬 단계에서 실패한 배치와 오류를 수집한다.
- [ ] 실패 배치를 순차적으로 한 번 재시도한다.
- [ ] 최종 실패가 남으면 실패 배치 수를 포함한 `BatchProcessingError`를 발생시킨다.
- [ ] fallback 테스트를 실행해 통과를 확인한다.

### Task 4: 의존성과 개발 문서 보완

**Files:**
- Modify: `requirements.txt`
- Modify: `README.md`
- Modify: `build.bat`

- [ ] `PyQt6`, `PyInstaller`를 Python 설치 목록에 추가한다.
- [ ] README에 개발 실행 및 빌드 전제 조건과 명령을 추가한다.
- [ ] `build.bat`의 CMD 괄호 충돌을 제거하고 전체 설치 파일 빌드를 실행한다.

### Task 5: 생성 파일 정리

**Files:**
- Modify: `.gitignore`
- Delete: `src/__pycache__/*.pyc`
- Delete: `stdout_test.txt`
- Delete: `stderr_test.txt`

- [ ] 테스트 로그의 정확한 파일명을 ignore 규칙에 추가한다.
- [ ] 이미 추적 중인 캐시와 로그를 제거한다.
- [ ] `git ls-files`로 생성 파일이 추적 대상에서 빠졌는지 확인한다.

### Task 6: 전체 검증

- [ ] `python -m unittest discover -s tests -v`를 실행한다.
- [ ] 모든 Python 파일을 AST로 파싱해 문법을 검사한다.
- [ ] `python src/main.py --help`의 종료 코드가 0인지 확인한다.
- [ ] kordoc의 실제 CLI를 샘플 문서에 실행해 파싱 경로를 확인한다.
- [ ] `git diff --check`와 `git status --short`로 최종 변경을 점검한다.
