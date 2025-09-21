import os
import shutil
import logging
from typing import Set, List
import config
from utils import (
    is_sensitive_file, should_hide_content, is_text_file,
    get_file_size, format_size, split_into_parts
)


def write_directory_structure(root_dir: str, exclude_dirs: Set[str]) -> List[str]:
    """Создает структуру директории и возвращает список файлов"""
    all_content_lines = []
    included_files = []
    total_files = 0
    total_size = 0

    for root, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        dirs.sort()
        files.sort()

        if files or dirs:
            rel_path = os.path.relpath(root, root_dir)
            level = rel_path.count(os.sep) if rel_path != "." else 0
            indent = "    " * level
            all_content_lines.append(f"{indent}{os.path.basename(root)}/")

            for i, file in enumerate(files):
                file_path = os.path.join(root, file)
                size_bytes, file_size = get_file_size(file_path)
                total_files += 1
                total_size += size_bytes
                connector = "└──" if i == len(files) - 1 and not dirs else "├──"
                all_content_lines.append(f"{indent}    {connector} {file} ({file_size})")
                included_files.append(file_path)

    total_size_readable = format_size(total_size)
    all_content_lines.append(f"\nTotal: {total_files} files, {total_size_readable}\n")
    all_content_lines.append("\n=== FILES CONTENT ===\n")

    return all_content_lines, included_files


def write_file_contents(root_dir: str, included_files: List[str], all_content_lines: List[str],
                        encoding: str, max_file_size: int) -> None:
    """Добавляет содержимое файлов в общий контент"""
    for file_path in included_files:
        if os.path.abspath(file_path) == os.path.abspath(config.OUTPUT_FILE):
            continue
        try:
            rel_path = os.path.relpath(file_path, root_dir)

            if is_sensitive_file(file_path):
                all_content_lines.append(f"-- File: {rel_path} -- [REDACTED: sensitive data]\n")
                continue

            if should_hide_content(file_path):
                all_content_lines.append(f"-- File: {rel_path} -- [CONTENT HIDDEN by config]\n")
                continue

            file_size = os.path.getsize(file_path)
            if file_size > max_file_size:
                all_content_lines.append(
                    f"-- File: {rel_path} -- [TOO LARGE: {format_size(file_size)} > {format_size(max_file_size)}]\n"
                )
                continue

            try:
                with open(file_path, "r", encoding=encoding, errors="strict") as file:
                    clean_lines, prev_empty = [], False
                    for raw_line in file:
                        line = raw_line.rstrip("\n")
                        if not line.strip():
                            if not prev_empty:
                                clean_lines.append("")
                            prev_empty = True
                        else:
                            clean_lines.append(line)
                            prev_empty = False

                    all_content_lines.append(f"-- File: {rel_path} --")
                    all_content_lines.extend(clean_lines)
                    all_content_lines.append("")

            except UnicodeDecodeError:
                all_content_lines.append(f"-- File: {rel_path} -- [BINARY CONTENT]\n")
        except IOError as e:
            rel_path = os.path.relpath(file_path, root_dir)
            logging.error(f"Ошибка чтения {rel_path}: {e}")


def write_project_data(
        root_dir: str = config.ROOT_DIR,
        output_file: str = config.OUTPUT_FILE,
        exclude_dirs: Set[str] = config.EXCLUDE_DIRS,
        encoding: str = config.ENCODING,
        max_file_size: int = config.MAX_FILE_SIZE,
) -> None:
    """Основная функция для создания экстракта проекта"""
    try:
        # Создаем структуру и получаем список файлов
        all_content_lines, included_files = write_directory_structure(root_dir, exclude_dirs)

        # Добавляем содержимое файлов
        write_file_contents(root_dir, included_files, all_content_lines, encoding, max_file_size)

        # Сохраняем основной файл
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, "w", encoding=encoding) as f:
            f.write("\n".join(all_content_lines))

        # Создаем части
        parts_dir = os.path.join(os.path.dirname(output_file), "parts")
        split_into_parts(all_content_lines, parts_dir)

        rel_parts_dir = os.path.relpath(parts_dir, root_dir)
        logging.info(f"Части кода записаны в папку: {rel_parts_dir}")

        # Если включен модульный режим - обрабатываем поддиректории рекурсивно
        if config.MODULAR_MODE:
            process_subdirectories_recursively(root_dir, os.path.dirname(output_file),
                                               exclude_dirs, encoding, max_file_size)

    except IOError as e:
        rel_output_path = os.path.relpath(output_file, root_dir)
        logging.error(f"Ошибка записи в {rel_output_path}: {e}")


def process_subdirectories_recursively(root_dir: str, output_base_dir: str,
                                       exclude_dirs: Set[str], encoding: str, max_file_size: int) -> None:
    """Рекурсивно обрабатывает все поддиректории"""
    for item in os.listdir(root_dir):
        item_path = os.path.join(root_dir, item)
        if os.path.isdir(item_path) and item not in exclude_dirs:
            # Создаем экстракт для поддиректории
            sub_output_dir = os.path.join(output_base_dir, item)
            sub_output_file = os.path.join(sub_output_dir, f"extract_{item}.txt")

            write_project_data(
                root_dir=item_path,
                output_file=sub_output_file,
                exclude_dirs=exclude_dirs,
                encoding=encoding,
                max_file_size=max_file_size
            )