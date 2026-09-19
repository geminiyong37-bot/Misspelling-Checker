# 맞춤법 검사기 신뢰성 보완 설계

## 목표

- CLI가 실제 AI 검사 함수 이름을 사용하도록 고친다.
- 개발 및 빌드 환경에서 `C:\MyProjects\Archive\kordoc`을 사용한다.
- 실행과 빌드에 필요한 Python 패키지를 설치 목록에 포함한다.
- 병렬 AI 검사에서 실패한 배치를 숨기지 않고 안전하게 재시도한다.
- Git에 들어간 Python 캐시와 대용량 테스트 로그를 제거하고 재등록을 막는다.

## 설계

### CLI

`src/main.py`는 존재하지 않는 `run_gemini_check` 대신 GUI와 동일한 `run_ai_check`를 호출한다. `--help`가 API 키나 문서를 요구하지 않고 정상 종료되는 것을 회귀 테스트로 확인한다.

### kordoc 경로

개발 환경의 기본 경로는 프로젝트 기준 `..\Archive\kordoc\dist\cli.cjs`다. `KORDOC_HOME` 환경변수가 있으면 해당 디렉터리를 우선 사용하고, PyInstaller 실행본은 번들 내부 `kordoc\dist\cli.cjs`를 사용한다. 실행 파일이 없을 때는 예상 경로와 해결 방법이 포함된 오류를 낸다.

PyInstaller 설정도 `..\Archive\kordoc`의 `dist`, `node_modules`, `package.json`을 번들에 포함하도록 맞춘다.
`build.bat`의 오류 처리 블록에서는 CMD 제어문과 충돌하지 않는 문구를 사용해 네 단계가 끝까지 실행되게 한다.

### AI 배치 fallback

첫 번째 단계는 기존처럼 최대 5개 배치를 병렬 처리한다. 실패한 배치만 모아 순차적으로 한 번 재시도한다. 재시도에도 실패한 배치가 하나라도 있으면 `BatchProcessingError`를 발생시켜 문서가 정상 완료로 표시되지 않게 한다. 성공한 배치의 결과만 조용히 반환하는 기존 동작은 제거한다.

### 의존성과 저장소 정리

`requirements.txt`에 GUI 실행용 `PyQt6`와 빌드용 `PyInstaller`를 추가한다. Inno Setup과 Node.js는 pip 패키지가 아니므로 README의 개발·빌드 요구사항으로 안내한다.

추적 중인 `src/__pycache__/*.pyc`, `stdout_test.txt`, `stderr_test.txt`는 저장소에서 제거한다. `.gitignore`에는 두 테스트 로그의 정확한 파일명을 추가해 문서용 TXT 파일에는 영향을 주지 않는다.

## 검증 기준

- `python src/main.py --help`가 종료 코드 0을 반환한다.
- `KORDOC_HOME` 지정 및 기본 Archive 경로가 모두 `cli.cjs`를 가리킨다.
- 최초 실패한 AI 배치가 fallback에서 성공하면 전체 결과가 반환된다.
- fallback도 실패하면 명확한 예외가 발생한다.
- 모든 Python 파일의 문법 검사와 전체 자동 테스트가 통과한다.
- 생성 파일이 더 이상 Git 추적 대상에 남지 않는다.
