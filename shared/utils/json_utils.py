import json
import re
from typing import Any, Tuple, Optional

_CODE_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)

def safe_parse_json(text: str) -> Tuple[Optional[Any], Optional[str]]:
    try:
        
        return json.loads(text), None
    
    except Exception:
        pass

    # 1) If it's in ```json ... ```, extract the inside
    m = _CODE_FENCE_RE.search(text)

    if m:
        candidate = m.group(1).strip()
        try:
            return json.loads(candidate), None
        except Exception as e:
            return None, f"JSON parsing failed after stripping code fences: {e}"

    # 2) Otherwise, try to extract the first {...} block
    start = text.find("{")
    end = text.rfind("}")
    
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1].strip()
        try:
            return json.loads(candidate), None
        except Exception as e:
            return None, f"JSON parsing failed after extracting object braces: {e}"

    return None, "No JSON object found in model output."