import pytest
from pathlib import Path
from unittest.mock import patch


def test_config_defaults():
    """Тестирует значения по умолчанию."""
    from config import ROOT_DIR, EXCLUDE_DIRS, SAFE_MODE

    # Получаем ожидаемый путь к корню проекта (на уровень выше tests/)
    expected_root = Path(__file__).parent.parent.resolve()

    # Проверяем что ROOT_DIR существует и является директорией
    assert ROOT_DIR.exists()
    assert ROOT_DIR.is_dir()

    # Проверяем другие значения по умолчанию
    assert '.venv' in EXCLUDE_DIRS
    assert SAFE_MODE is True

def test_config_from_env(monkeypatch):
    """Тестирует загрузку из окружения."""
    monkeypatch.setenv('ROOT_DIR', 'test/path')  # относительный путь
    monkeypatch.setenv('EXCLUDE_DIRS', 'test1,test2')
    monkeypatch.setenv('SAFE_MODE', 'false')

    from importlib import reload
    import config
    reload(config)

    assert config.ROOT_DIR == Path('test/path').resolve()
    assert config.EXCLUDE_DIRS == {'test1', 'test2'}
    assert config.SAFE_MODE is False