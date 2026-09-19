import os
import re

import sys

def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative)

RAG_DOC_PATH = resource_path(os.path.join("docs", "공문서_지침_압축.txt"))

def normalize_text(value):
    if not value:
        return ""
    # 은어/개행 처리 및 공백 제거
    lines = value.replace("\r\n", "\n").split("\n")
    return "\n".join([line.strip() for line in lines if line.strip()])

def get_rag_instruction_text():
    if not os.path.exists(RAG_DOC_PATH):
        print(f"경고: RAG 지침 파일을 찾을 수 없습니다: {RAG_DOC_PATH}")
        return ""
    
    try:
        with open(RAG_DOC_PATH, "r", encoding="utf-8") as f:
            raw = f.read()
        return normalize_text(raw)
    except Exception as e:
        print(f"오류: RAG 파일을 읽는 중 문제가 발생했습니다: {e}")
        return ""

OPTION_SECTION_MAP = {
    "check_date_format": (1, 2, 3),
    "suggest_plain_language": (7,),
    "improve_style": (8,),
}


def get_rag_instruction_sections():
    text = get_rag_instruction_text()
    if not text:
        return {}
    matches = re.finditer(
        r"(?ms)^(\d+)\.\s+.*?(?=^\d+\.\s+|\Z)",
        text,
    )
    return {int(match.group(1)): match.group(0).strip() for match in matches}


def build_rag_prompt_section(review_options=None):
    options = review_options or {}
    selected_numbers = []
    for option_name, section_numbers in OPTION_SECTION_MAP.items():
        if options.get(option_name):
            selected_numbers.extend(section_numbers)
    if not selected_numbers:
        return ""

    sections = get_rag_instruction_sections()
    selected_text = [sections[number] for number in selected_numbers if number in sections]
    if not selected_text:
        return ""
    return "\n[선택 검사 모드 지침]\n" + "\n\n".join(selected_text) + "\n"
