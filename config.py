import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Основные настройки
ROOT_DIR = Path(os.getenv("ROOT_DIR", ".")).resolve()
EXCLUDE_DIRS = set(os.getenv("EXCLUDE_DIRS", ".venv,__pycache__").split(","))
HIDE_FILE_CONTENTS = set(os.getenv("HIDE_FILE_CONTENTS", "").split(","))
ENCODING = os.getenv("ENCODING", "utf-8")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "1048576"))  # 1MB
SAFE_MODE = os.getenv("SAFE_MODE", "true").lower() == "true"
SENSITIVE_FILES = set(os.getenv("SENSITIVE_FILES", ".env,.env.*,*.key,*.secret,config.json").split(","))
PART_LINES_LIMIT = int(os.getenv("PART_LINES_LIMIT", 500))
MODULAR_MODE = os.getenv("MODULAR_MODE", "false").lower() == "true"

PROJECT_NAME = ROOT_DIR.name

# Пути для вывода с использованием pathlib
OUT_DIR = Path(__file__).parent / "out"
PROJECT_OUTPUT_DIR = OUT_DIR / PROJECT_NAME
PARTS_DIR = PROJECT_OUTPUT_DIR / "parts"
OUTPUT_FILE = PROJECT_OUTPUT_DIR / f"extract_{PROJECT_NAME}.txt"