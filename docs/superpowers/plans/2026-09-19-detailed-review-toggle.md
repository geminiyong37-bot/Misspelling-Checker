# Detailed Review Toggle Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace three optional review checkboxes with one subtle `추가 상세 검사` checkbox at the top right.

**Architecture:** `MainWindow` owns one `cb_detailed_review` widget. Its checked state is adapted to the three existing AI option keys in `get_review_options()`, so downstream inspection code remains unchanged.

**Tech Stack:** Python, PyQt6, unittest, PyInstaller, Inno Setup

---

### Task 1: Specify the single-checkbox behavior

**Files:**
- Modify: `tests/test_app_options.py:26-52`

- [ ] **Step 1: Replace the old UI test with failing tests**

```python
def test_detailed_review_is_the_only_optional_checkbox_and_is_off_by_default(self):
    window = app.MainWindow()
    try:
        self.assertEqual(window.cb_detailed_review.text(), "추가 상세 검사")
        self.assertFalse(window.cb_detailed_review.isChecked())
        self.assertFalse(hasattr(window, "cb_date_format"))
        self.assertFalse(hasattr(window, "cb_plain_language"))
        self.assertFalse(hasattr(window, "cb_style"))
    finally:
        window.close()

def test_detailed_review_controls_all_optional_modes(self):
    window = app.MainWindow()
    try:
        self.assertEqual(window.get_review_options(), {
            "check_date_format": False,
            "suggest_plain_language": False,
            "improve_style": False,
        })
        window.cb_detailed_review.setChecked(True)
        self.assertEqual(window.get_review_options(), {
            "check_date_format": True,
            "suggest_plain_language": True,
            "improve_style": True,
        })
    finally:
        window.close()

def test_detailed_review_uses_the_same_font_size_as_drop_hint(self):
    window = app.MainWindow()
    try:
        self.assertEqual(window.cb_detailed_review.property("textSize"), "subtle")
        self.assertEqual(window.drop_area.drop_hint.property("textSize"), "subtle")
    finally:
        window.close()
```

- [ ] **Step 2: Run the focused tests and verify failure**

Run: `python -m unittest tests.test_app_options.ReviewOptionsUiTests -v`

Expected: FAIL because `cb_detailed_review` and `drop_hint` do not exist yet.

### Task 2: Implement the top-right toggle

**Files:**
- Modify: `src/app.py:196-205`
- Modify: `src/app.py:466-560`
- Modify: `src/app.py:590-610`
- Modify: `src/app.py:801-810`

- [ ] **Step 1: Expose the drop hint and give subtle text a shared property**

```python
self.drop_hint = QLabel("또는 아래 버튼을 눌러 선택")
self.drop_hint.setAlignment(Qt.AlignmentFlag.AlignHCenter)
self.drop_hint.setProperty("textSize", "subtle")
```

- [ ] **Step 2: Replace the title and options frame with one header row**

```python
header_row = QGridLayout()
title = QLabel("문서 맞춤법 검사기")
title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
title.setObjectName("headerTitle")
header_row.addWidget(title, 0, 0, 1, 3)
self.cb_detailed_review = QCheckBox("추가 상세 검사")
self.cb_detailed_review.setChecked(False)
self.cb_detailed_review.setProperty("textSize", "subtle")
self.cb_detailed_review.setToolTip(
    "날짜·숫자 표기, 순화어, 문체·표현을 함께 추가 검사합니다."
)
header_row.addWidget(
    self.cb_detailed_review, 0, 2, alignment=Qt.AlignmentFlag.AlignRight
)
```

Remove `options_frame`, `options_title`, `cb_date_format`, `cb_plain_language`, and `cb_style`. Add `header_row` to the root layout instead of the old title widget, and do not add an options frame.

- [ ] **Step 3: Apply one non-emphasized text style**

```css
*[textSize="subtle"] { font-size: 10px; font-weight: 400; color: #5D4037; }
```

Remove the obsolete `#dropHint`, `#optionsFrame`, and `#optionsTitle` rules.

- [ ] **Step 4: Adapt the one state to all existing option keys**

```python
def get_review_options(self):
    detailed_review = self.cb_detailed_review.isChecked()
    return {
        "check_date_format": detailed_review,
        "suggest_plain_language": detailed_review,
        "improve_style": detailed_review,
    }

def _set_review_options_enabled(self, enabled):
    self.cb_detailed_review.setEnabled(enabled)
```

- [ ] **Step 5: Run the focused tests and verify success**

Run: `python -m unittest tests.test_app_options.ReviewOptionsUiTests -v`

Expected: all `ReviewOptionsUiTests` pass.

### Task 3: Verify and package

**Files:**
- Verify: `src/app.py`
- Verify: `tests/test_app_options.py`
- Generated: `Output/AI_Word_Speller_Setup.exe`

- [ ] **Step 1: Run the complete test suite**

Run: `python -m unittest discover -s tests -v`

Expected: all tests pass.

- [ ] **Step 2: Check the diff**

Run: `git diff --check`

Expected: no output and exit code 0.

- [ ] **Step 3: Build the installer**

Run: `cmd.exe /d /c build.bat`

Expected: PyInstaller and Inno Setup finish successfully and create `Output/AI_Word_Speller_Setup.exe`.

- [ ] **Step 4: Commit the implementation**

```powershell
git add -- src/app.py tests/test_app_options.py docs/superpowers/plans/2026-09-19-detailed-review-toggle.md Output/AI_Word_Speller_Setup.exe
git commit -m "feat: simplify detailed review options"
```
