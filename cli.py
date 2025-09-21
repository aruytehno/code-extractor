import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Code Extractor: утилита для экспорта структуры и содержимого проекта"
    )

    parser.add_argument(
        "--root",
        type=str,
        help="Путь к корню проекта (переопределяет ROOT_DIR из .env)"
    )

    parser.add_argument(
        "--safe",
        type=str,
        choices=["true", "false"],
        help="Включить/выключить SAFE_MODE (переопределяет SAFE_MODE из .env)"
    )

    parser.add_argument(
        "--max-size",
        type=str,
        help="Максимальный размер файла для чтения (например: 2MB, 500KB, 1000000)"
    )

    parser.add_argument(
        "--encoding",
        type=str,
        help="Кодировка файлов (по умолчанию utf-8)"
    )

    parser.add_argument(
        "--exclude",
        type=str,
        help="Список папок для исключения через запятую"
    )

    return parser.parse_args()


def parse_size(value: str) -> int:
    """Парсим значения с суффиксами MB/KB/B"""
    units = {"kb": 1024, "mb": 1024 * 1024, "b": 1}
    value = value.strip().lower()
    for unit, factor in units.items():
        if value.endswith(unit):
            return int(float(value.replace(unit, "")) * factor)
    return int(value)  # если просто число
