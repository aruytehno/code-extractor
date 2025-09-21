import pytest
from unittest.mock import mock_open, patch
from utils import is_sensitive_file, should_hide_content, format_size, get_file_size, split_into_parts


def test_is_sensitive_file(mock_config):
    """Тестирует определение чувствительных файлов."""
    assert is_sensitive_file('/fake/path/.env.secret') is True
    assert is_sensitive_file('/fake/path/config.secret') is True
    assert is_sensitive_file('/fake/path/normal.py') is False


def test_should_hide_content(mock_config):
    """Тестирует определение файлов с скрываемым содержимым."""
    assert should_hide_content('/fake/path/config.json') is True
    assert should_hide_content('/fake/path/normal.py') is False


def test_format_size():
    """Тестирует форматирование размера файла."""
    assert format_size(500) == "500 B"
    assert format_size(2048) == "2.0 KB"
    assert format_size(3145728) == "3.0 MB"


def test_get_file_size(temp_dir):
    """Тестирует получение размера файла."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("Hello")

    size, readable = get_file_size(str(test_file))
    assert size == 5
    assert readable == "5 B"


def test_split_into_parts():
    """Тестирует разделение контента на части."""
    lines = [f"Line {i}" for i in range(1000)]

    with patch('utils.config') as mock_config:
        mock_config.PART_LINES_LIMIT = 100
        mock_config.ENCODING = 'utf-8'

        with patch('builtins.open', mock_open()) as mock_file:
            split_into_parts(lines, '/fake/path')

            # Проверяем, что файлы созданы
            assert mock_file.call_count == 10


def test_is_text_file(temp_dir):
    """Тестирует определение текстовых файлов."""
    from utils import is_text_file

    # Текстовый файл
    text_file = temp_dir / "text.txt"
    text_file.write_text("Hello World")
    assert is_text_file(str(text_file), 'utf-8') is True

    # Бинарный файл
    binary_file = temp_dir / "binary.bin"
    png_header = bytes([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A])
    binary_file.write_bytes(png_header)
    assert is_text_file(str(binary_file), 'utf-8') is False


def test_is_text_file_edge_cases(temp_dir):
    """Тестирует edge cases для определения текстовых файлов."""
    from utils import is_text_file

    # Пустой файл
    empty_file = temp_dir / "empty.txt"
    empty_file.write_text("")
    assert is_text_file(str(empty_file), 'utf-8') is True

    # Файл с только пробелами
    spaces_file = temp_dir / "spaces.txt"
    spaces_file.write_text("   \n   \t   ")
    assert is_text_file(str(spaces_file), 'utf-8') is True

    # Файл с не UTF-8 контентом но без нулевых байтов
    non_utf8_file = temp_dir / "non_utf8.txt"
    non_utf8_file.write_bytes(b"\xFF\xFE\xFD")  # Invalid UTF-8
    assert is_text_file(str(non_utf8_file), 'utf-8') is False


def test_format_size_edge_cases():
    """Тестирует edge cases для форматирования размеров."""
    from utils import format_size

    # Байты
    assert format_size(0) == "0 B"
    assert format_size(1) == "1 B"
    assert format_size(1023) == "1023 B"

    # Килобайты
    assert format_size(1024) == "1.0 KB"
    assert format_size(1024 + 512) == "1.5 KB"  # Половина килобайта
    assert format_size(1024 * 1024 - 1) == "1024.0 KB"  # Ещё в KB

    # Мегабайты
    assert format_size(1024 * 1024) == "1.0 MB"
    assert format_size(1024 * 1024 + 512 * 1024) == "1.5 MB"
    assert format_size(1024 ** 3 - 1) == "1024.0 MB"  # До GB

    # Гигабайты
    assert format_size(1024 ** 3) == "1.0 GB"
    assert format_size(1024 ** 3 + 512 * 1024 ** 2) == "1.5 GB"
    assert format_size(1024 ** 4 - 1) == "1024.0 GB"  # До TB

    # Терабайты
    assert format_size(1024 ** 4) == "1.0 TB"
    assert format_size(1024 ** 4 + 512 * 1024 ** 3) == "1.5 TB"


def test_split_into_parts_edge_cases():
    """Тестирует edge cases для разделения на части."""
    from utils import split_into_parts

    # Пустой список
    with patch('utils.config') as mock_config, \
            patch('builtins.open', mock_open()):
        mock_config.PART_LINES_LIMIT = 100
        mock_config.ENCODING = 'utf-8'

        split_into_parts([], '/fake/path')
        # Не должно упасть


def test_get_file_size_nonexistent():
    """Тестирует получение размера несуществующего файла."""
    from utils import get_file_size

    size, readable = get_file_size('/nonexistent/path/file.txt')
    assert size == 0
    assert readable == "0 B"


def test_is_text_file_empty(temp_dir):
    """Тестирует определение пустых файлов как текстовых."""
    from utils import is_text_file  # Добавляем импорт

    empty_file = temp_dir / "empty.txt"
    empty_file.write_text("")
    assert is_text_file(str(empty_file), 'utf-8') is True