import tempfile
import pytest
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Создает временную директорию для тестов."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_project_structure(temp_dir):
    """Создает тестовую структуру проекта."""
    # Создаем основные файлы
    (temp_dir / "main.py").write_text("print('Hello World')")
    (temp_dir / "config.json").write_text('{"key": "value"}')
    (temp_dir / ".env.secret").write_text("SECRET=password")
    (temp_dir / "binary_file.bin").write_bytes(b"\x00\x01\x02\x03")

    # Создаем поддиректорию
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    (subdir / "helper.py").write_text("def help():\n    return True")

    # Создаем файл для исключения
    exclude_dir = temp_dir / "exclude_me"
    exclude_dir.mkdir()
    (exclude_dir / "ignored.py").write_text("print('ignored')")

    return temp_dir


@pytest.fixture
def mock_config(monkeypatch):
    """Мокирует конфигурацию для тестов."""
    monkeypatch.setattr('config.ROOT_DIR', Path('/fake/path'))
    monkeypatch.setattr('config.EXCLUDE_DIRS', {'exclude_me'})
    monkeypatch.setattr('config.SENSITIVE_FILES', {'.env.secret', '*.secret'})
    monkeypatch.setattr('config.HIDE_FILE_CONTENTS', {'*.json'})
    monkeypatch.setattr('config.SAFE_MODE', True)
    monkeypatch.setattr('config.MAX_FILE_SIZE', 1024)
    monkeypatch.setattr('config.ENCODING', 'utf-8')