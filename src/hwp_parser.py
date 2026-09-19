import subprocess
import json
import os
import sys

def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative)

def get_kordoc_path():
    """현재 실행 환경에서 사용할 kordoc CLI 경로를 반환한다."""
    if hasattr(sys, '_MEIPASS'):
        return resource_path(os.path.join("kordoc", "dist", "cli.cjs"))

    kordoc_home = os.environ.get("KORDOC_HOME")
    if not kordoc_home:
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        kordoc_home = os.path.abspath(os.path.join(project_root, "..", "Archive", "kordoc"))

    return os.path.join(kordoc_home, "dist", "cli.cjs")


KORDOC_PATH = get_kordoc_path()


def parse_with_kordoc(file_path):
    """
    Parses a document (HWP, HWPX, PDF, DOCX) using kordoc CLI, 
    or reads directly if it's a plain text files (.txt).
    """
    abs_path = os.path.abspath(file_path)
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"File not found: {abs_path}")

    ext = os.path.splitext(abs_path)[1].lower()

    # 1. Plain text handling
    if ext == '.txt':
        content = ""
        # Try utf-8 first, fallback to cp949
        for enc in ['utf-8', 'cp949', 'euc-kr']:
            try:
                with open(abs_path, 'r', encoding=enc) as f:
                    content = f.read()
                break
            except UnicodeDecodeError:
                continue
        
        # Build kordoc-compatible JSON structure
        return {
            "blocks": [
                {
                    "type": "paragraph",
                    "text": content,
                    "pageNumber": 1
                }
            ],
            "fileType": "txt"
        }

    # 2. kordoc CLI handling (HWP, HWPX, PDF, DOCX)
    kordoc_path = get_kordoc_path()
    if not os.path.isfile(kordoc_path):
        raise FileNotFoundError(
            "kordoc CLI를 찾을 수 없습니다: "
            f"{kordoc_path}. C:\\MyProjects\\Archive\\kordoc을 확인하거나 "
            "KORDOC_HOME 환경변수를 설정해 주세요."
        )

    cmd = ["node", kordoc_path, abs_path, "--format", "json"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', check=True)
        stdout = result.stdout
        
        # Extract JSON part (in case kordoc prints progress to stdout)
        start_idx = stdout.find('{')
        end_idx = stdout.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            json_str = stdout[start_idx:end_idx + 1]
            return json.loads(json_str)
        else:
            return json.loads(stdout) # Fallback to original
    except subprocess.CalledProcessError as e:
        # kordoc might exit with error for unsupported formats like .doc
        error_msg = e.stderr or e.stdout
        print(f"Error executing kordoc: {error_msg}", file=sys.stderr)
        raise Exception(f"문서 파싱 실패 (kordoc): {error_msg}")
    except json.JSONDecodeError as e:
        print(f"Failed to parse kordoc output as JSON: {e}", file=sys.stderr)
        raise
