# AI Provider Models and Structured Output Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Upgrade the three default AI models, allow provider-specific environment overrides, enforce one dynamic JSON Schema across providers, and show the selected models during API-key setup.

**Architecture:** Keep the existing provider detection and REST endpoints. Add a model resolver and a shared schema builder in `ai_client.py`, pass the schema through the existing prompt payload, and adapt each provider request to its native structured-output field. Keep semantic validation in `parse_errors` and expose two pure UI text helpers so model labels can be tested without opening dialogs.

**Tech Stack:** Python 3.14, `requests`, PyQt6, `unittest`, PyInstaller, Inno Setup

---

## File map

- Modify `src/ai_client.py`: default models, environment overrides, shared JSON Schema, provider payloads.
- Modify `src/app.py`: API-key prompt and confirmation text showing resolved models.
- Modify `tests/test_ai_client.py`: model resolution, schema, and provider request payload regression tests.
- Modify `tests/test_app_options.py`: API-key setup text regression tests.
- Rebuild `Output/AI_Word_Speller_Setup.exe`: package the verified changes.

### Task 1: Model resolution and shared response schema

**Files:**
- Modify: `src/ai_client.py:10-100`
- Test: `tests/test_ai_client.py`

- [ ] **Step 1: Write failing model and schema tests**

Add tests that require the new defaults, environment overrides, and option-dependent schema:

```python
class ModelAndSchemaTests(unittest.TestCase):
    def test_default_models_are_current_stable_choices(self):
        self.assertEqual(ai_client.MODEL_MAP[ai_client.PROVIDER_GEMINI], "gemini-3.8-flash")
        self.assertEqual(ai_client.MODEL_MAP[ai_client.PROVIDER_OPENAI], "gpt-5.6-terra")
        self.assertEqual(
            ai_client.MODEL_MAP[ai_client.PROVIDER_ANTHROPIC],
            "claude-haiku-4-5-20251001",
        )

    def test_provider_model_environment_override_wins(self):
        with patch.dict(os.environ, {"TYPO_OPENAI_MODEL": "custom-openai"}):
            self.assertEqual(
                ai_client.get_provider_model(ai_client.PROVIDER_OPENAI),
                "custom-openai",
            )

    def test_blank_model_override_uses_default(self):
        with patch.dict(os.environ, {"TYPO_GEMINI_MODEL": "   "}):
            self.assertEqual(
                ai_client.get_provider_model(ai_client.PROVIDER_GEMINI),
                "gemini-3.8-flash",
            )

    def test_response_schema_uses_enabled_error_types(self):
        schema = ai_client.build_error_response_schema({"improve_style": True})
        error_schema = schema["properties"]["errors"]["items"]
        self.assertEqual(
            set(error_schema["properties"]["errorType"]["enum"]),
            {"spelling", "spacing", "word_choice", "style"},
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(error_schema["additionalProperties"])
```

- [ ] **Step 2: Run the focused tests and verify RED**

Run:

```powershell
python -m unittest tests.test_ai_client.ModelAndSchemaTests -v
```

Expected: failures for the old model values and missing `get_provider_model` / `build_error_response_schema`.

- [ ] **Step 3: Implement model resolution and the shared schema**

In `src/ai_client.py`, set the defaults and add:

```python
MODEL_MAP = {
    PROVIDER_GEMINI: "gemini-3.8-flash",
    PROVIDER_OPENAI: "gpt-5.6-terra",
    PROVIDER_ANTHROPIC: "claude-haiku-4-5-20251001",
}

MODEL_ENV_MAP = {
    PROVIDER_GEMINI: "TYPO_GEMINI_MODEL",
    PROVIDER_OPENAI: "TYPO_OPENAI_MODEL",
    PROVIDER_ANTHROPIC: "TYPO_ANTHROPIC_MODEL",
}


def get_provider_model(provider):
    override = os.environ.get(MODEL_ENV_MAP[provider], "").strip()
    return override or MODEL_MAP[provider]


def build_error_response_schema(review_options=None):
    allowed_types = sorted(get_allowed_error_types(review_options))
    error_properties = {
        "page": {"type": "integer"},
        "sentence": {"type": "string"},
        "original": {"type": "string"},
        "corrected": {"type": "string"},
        "reason": {"type": "string"},
        "errorType": {"type": "string", "enum": allowed_types},
    }
    return {
        "type": "object",
        "properties": {
            "errors": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": error_properties,
                    "required": list(error_properties),
                    "additionalProperties": False,
                },
            }
        },
        "required": ["errors"],
        "additionalProperties": False,
    }
```

Add `"response_schema": build_error_response_schema(review_options)` to `build_prompt_payload`.

- [ ] **Step 4: Run the focused tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_ai_client.ModelAndSchemaTests -v
```

Expected: all `ModelAndSchemaTests` pass.

### Task 2: Provider-native structured outputs

**Files:**
- Modify: `src/ai_client.py:150-310`
- Test: `tests/test_ai_client.py`

- [ ] **Step 1: Write failing provider payload tests**

Add a response stub and one test for each REST payload:

```python
class FakeResponse:
    status_code = 200
    text = ""

    def __init__(self, data):
        self._data = data

    def json(self):
        return self._data


class ProviderStructuredOutputTests(unittest.TestCase):
    def setUp(self):
        self.schema = ai_client.build_error_response_schema({})

    def test_gemini_sends_response_json_schema(self):
        session = unittest.mock.Mock()
        session.post.return_value = FakeResponse(
            {"candidates": [{"content": {"parts": [{"text": '{"errors":[]}' }]}}]}
        )
        with patch.object(ai_client, "get_session", return_value=session):
            ai_client.call_gemini("prompt", "key", response_schema=self.schema)
        body = session.post.call_args.kwargs["json"]
        url = session.post.call_args.args[0]
        self.assertIn("gemini-3.8-flash:generateContent", url)
        self.assertEqual(body["generationConfig"]["responseJsonSchema"], self.schema)

    def test_openai_uses_strict_json_schema(self):
        session = unittest.mock.Mock()
        session.post.return_value = FakeResponse(
            {"choices": [{"message": {"content": '{"errors":[]}'}}]}
        )
        with patch.object(ai_client, "get_session", return_value=session):
            ai_client.call_openai("system", "user", "key", response_schema=self.schema)
        body = session.post.call_args.kwargs["json"]
        json_schema = body["response_format"]["json_schema"]
        self.assertEqual(body["model"], "gpt-5.6-terra")
        self.assertTrue(json_schema["strict"])
        self.assertEqual(json_schema["schema"], self.schema)

    def test_anthropic_uses_output_config_schema(self):
        session = unittest.mock.Mock()
        session.post.return_value = FakeResponse(
            {"content": [{"type": "text", "text": '{"errors":[]}'}]}
        )
        with patch.object(ai_client, "get_session", return_value=session):
            ai_client.call_anthropic("system", "user", "key", response_schema=self.schema)
        body = session.post.call_args.kwargs["json"]
        self.assertEqual(body["model"], "claude-haiku-4-5-20251001")
        self.assertEqual(body["output_config"]["format"]["schema"], self.schema)
```

- [ ] **Step 2: Run the provider tests and verify RED**

Run:

```powershell
python -m unittest tests.test_ai_client.ProviderStructuredOutputTests -v
```

Expected: failures because provider functions do not accept `response_schema` and still use old output configuration.

- [ ] **Step 3: Implement provider payload changes**

Change provider function signatures to resolve the model at call time:

```python
def call_gemini(prompt_text, api_key, model=None, response_schema=None):
    model = model or get_provider_model(PROVIDER_GEMINI)
    # Keep existing URL and response parsing.

def call_openai(system_prompt, user_text, api_key, model=None, response_schema=None):
    model = model or get_provider_model(PROVIDER_OPENAI)
    # Keep existing headers and response parsing.

def call_anthropic(system_prompt, user_text, api_key, model=None, response_schema=None):
    model = model or get_provider_model(PROVIDER_ANTHROPIC)
    # Keep existing headers and response parsing.
```

Use these exact provider fields:

```python
# Gemini generationConfig
"responseMimeType": "application/json",
"responseJsonSchema": response_schema,

# OpenAI Chat Completions
"response_format": {
    "type": "json_schema",
    "json_schema": {
        "name": "spelling_check_result",
        "strict": True,
        "schema": response_schema,
    },
},

# Anthropic Messages
"output_config": {
    "format": {
        "type": "json_schema",
        "schema": response_schema,
    }
},
```

Pass `payload["response_schema"]` from `_call_provider` to the selected call. Provider calls used by `validate_api_key` receive the same schema from `build_prompt_payload`.

- [ ] **Step 4: Run provider and fallback tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_ai_client.ProviderStructuredOutputTests tests.test_ai_client.AiFallbackTests -v
```

Expected: provider payload and fallback tests pass.

- [ ] **Step 5: Commit the model and provider changes**

Run:

```powershell
git add -- src/ai_client.py tests/test_ai_client.py
git commit -m "feat: upgrade AI models and structured outputs"
```

Expected: one commit containing only AI client behavior and its tests.

### Task 3: Show resolved models during API-key setup

**Files:**
- Modify: `src/app.py:20-75, 600-640`
- Test: `tests/test_app_options.py`

- [ ] **Step 1: Write failing text-helper tests**

Add tests for the API-key prompt and confirmation:

```python
class ApiKeyModelTextTests(unittest.TestCase):
    def test_api_key_prompt_lists_all_default_models(self):
        text = app.build_api_key_prompt_text()
        self.assertIn("Gemini — gemini-3.8-flash", text)
        self.assertIn("OpenAI — gpt-5.6-terra", text)
        self.assertIn("Anthropic — claude-haiku-4-5-20251001", text)

    def test_confirmation_uses_environment_override(self):
        with patch.dict(os.environ, {"TYPO_OPENAI_MODEL": "custom-openai"}):
            text = app.build_api_key_confirmation_text(app.PROVIDER_OPENAI)
        self.assertIn("공급자: openai", text)
        self.assertIn("모델: custom-openai", text)
```

Import `patch` from `unittest.mock` in the test file.

- [ ] **Step 2: Run the UI text tests and verify RED**

Run:

```powershell
python -m unittest tests.test_app_options.ApiKeyModelTextTests -v
```

Expected: failures because the two pure text helpers do not exist.

- [ ] **Step 3: Implement pure text helpers and wire them into the dialog**

Import `get_provider_model` from `ai_client` and add:

```python
def build_api_key_prompt_text():
    return (
        "API 키를 입력해 주세요.\n\n"
        f"Gemini — {get_provider_model(PROVIDER_GEMINI)}\n"
        f"OpenAI — {get_provider_model(PROVIDER_OPENAI)}\n"
        f"Anthropic — {get_provider_model(PROVIDER_ANTHROPIC)}"
    )


def build_api_key_confirmation_text(provider):
    return f"API 키가 설정되었습니다.\n공급자: {provider}\n모델: {get_provider_model(provider)}"
```

Use `build_api_key_prompt_text()` in `QInputDialog.getText` and `build_api_key_confirmation_text(new_provider)` in the success message.

- [ ] **Step 4: Run the UI tests and verify GREEN**

Run:

```powershell
python -m unittest tests.test_app_options -v
```

Expected: all UI option and API-key text tests pass.

- [ ] **Step 5: Commit the API-key model labels**

Run:

```powershell
git add -- src/app.py tests/test_app_options.py
git commit -m "feat: show selected models during API key setup"
```

Expected: one commit containing the API-key text helpers, dialog wiring, and tests.

### Task 4: Full regression verification and installer

**Files:**
- Verify: `src/ai_client.py`, `src/app.py`, `tests/`
- Build: `Output/AI_Word_Speller_Setup.exe`

- [ ] **Step 1: Run the full test suite**

Run:

```powershell
python -m unittest discover -s tests -v
```

Expected: all tests pass with zero failures and errors.

- [ ] **Step 2: Compile and inspect the diff**

Run:

```powershell
python -m compileall -q src tests
git diff --check
```

Expected: both commands exit 0; only existing line-ending warnings may appear.

- [ ] **Step 3: Build the installer**

Run:

```powershell
cmd.exe /d /c build.bat
```

Expected: exit 0 and `Output\AI_Word_Speller_Setup.exe` is regenerated.

- [ ] **Step 4: Record installer identity**

Run:

```powershell
Get-Item Output\AI_Word_Speller_Setup.exe | Select-Object FullName, Length, LastWriteTime
Get-FileHash -Algorithm SHA256 Output\AI_Word_Speller_Setup.exe
```

Expected: a nonzero file size, current timestamp, and SHA256 hash.

- [ ] **Step 5: Review status without staging unrelated changes**

Run:

```powershell
git status --short
git diff -- src/ai_client.py src/app.py tests/test_ai_client.py tests/test_app_options.py
```

Expected: only the intended implementation and pre-existing workspace changes are reported; no generated build artifacts are tracked.
