import os
import fnmatch
import logging
from typing import List, Tuple
import config


def is_sensitive_file(file_path: str) -> bool:
    filename = os.path.basename(file_path)
    return config.SAFE_MODE and any(fnmatch.fnmatch(filename, pattern) for pattern in config.SENSITIVE_FILES)


def should_hide_content(file_path: str) -> bool:
    filename = os.path.basename(file_path)
    return any(fnmatch.fnmatch(filename, pattern) for pattern in config.HIDE_FILE_CONTENTS)


def is_text_file(file_path: str, encoding: str) -> bool:
    """
    Определяет, является ли файл текстовым.
    Более надежная проверка через анализ содержимого.
    """
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(1024)
            # Пустой файл считается текстовым
            if not sample:
                return True

            # Пытаемся декодировать с разными стратегиями ошибок
            try:
                sample.decode(encoding, errors='strict')
                return True
            except UnicodeDecodeError:
                # Проверяем наличие нулевых байтов - признак бинарного файла
                if b'\x00' in sample:
                    return False
                # Пробуем с более мягкой обработкой ошибок
                try:
                    sample.decode(encoding, errors='replace')
                    # Если много замененных символов, вероятно бинарный
                    decoded = sample.decode(encoding, errors='replace')
                    if decoded.count('�') / len(decoded) > 0.1:  # Более 10% замен
                        return False
                    return True
                except:
                    return False
    except Exception:
        return False


def format_size(size: int) -> str:
    """Форматирует размер в удобочитаемую строку с B, KB, MB, GB, TB."""
    units = ["B", "KB", "MB", "GB", "TB"]
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024
        index += 1
    if units[index] == "B":
        return f"{int(size)} {units[index]}"
    else:
        return f"{size:.1f} {units[index]}"



def get_file_size(file_path: str) -> Tuple[int, str]:
    try:
        size = os.path.getsize(file_path)
        return size, format_size(size)
    except OSError:
        return 0, "0 B"


def split_into_parts(all_lines: List[str], part_dir: str, part_prefix: str = "part") -> None:
    os.makedirs(part_dir, exist_ok=True)

    # Вычисляем общее количество частей
    total_parts = (len(all_lines) + config.PART_LINES_LIMIT - 1) // config.PART_LINES_LIMIT

    for part_num in range(1, total_parts + 1):
        start_idx = (part_num - 1) * config.PART_LINES_LIMIT
        end_idx = part_num * config.PART_LINES_LIMIT
        part_lines = all_lines[start_idx:end_idx]

        part_file = os.path.join(part_dir, f"{part_prefix}_{part_num}.txt")
        with open(part_file, "w", encoding=config.ENCODING) as pf:
            if part_num < total_parts:
                pf.write(f"### НЕ ОТВЕЧАЙ, ЖДИ ВСЕ ЧАСТИ КОДА ПРОЕКТА. ЧАСТЬ {part_num} ИЗ {total_parts} ###\n\n")
            else:
                pf.write(f"### ВСЕ ЧАСТИ КОДА ПРОЕКТА ПЕРЕДАНЫ. ЧАСТЬ {part_num} ИЗ {total_parts} ###\n\n")
            pf.write("\n".join(part_lines))

        rel_part_file = os.path.relpath(part_file, config.ROOT_DIR)
        logging.info(f"Создана часть: {rel_part_file} ({part_num}/{total_parts})")
