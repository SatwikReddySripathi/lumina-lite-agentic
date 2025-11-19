import re
from typing import Dict, Tuple

HARMFUL_PATTERNS = [
    r"(?i)(hack|exploit|vulnerability|malware|virus)",
    r"(?i)(sql injection|xss|ddos)",
    r"(?i)(personal data|ssn|credit card)",
]


def check_input_safety(text: str) -> Tuple[bool, str]:
    if not text or len(text.strip()) < 3:
        return False, "Input too short"
    
    if len(text) > 10000:
        return False, "Input too long (max 10,000 chars)"
    
    for pattern in HARMFUL_PATTERNS:
        if re.search(pattern, text):
            return False, "Input contains potentially harmful content"
    
    return True, "OK"


def check_output_quality(text: str, min_length: int = 50) -> Tuple[bool, str]:

    if not text or len(text.strip()) < min_length:
        return False, f"Output too short (min {min_length} chars)"
    
    if "I cannot" in text or "I'm unable to" in text:
        return False, "Model declined to answer"
    
    return True, "OK"


def sanitize_file_path(path: str) -> str:

    path = path.replace("..", "").replace("~", "")
    path = re.sub(r'[^a-zA-Z0-9\-_./\\]', '', path)
    return path