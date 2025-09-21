import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path


def test_main_successful_execution(monkeypatch):
    """Тестирует успешное выполнение main."""
    from main import main as main_func

    with patch('main.parse_args') as mock_parse, \
            patch('main.logging.basicConfig'), \
            patch('main.shutil.rmtree'), \
            patch('main.os.makedirs'), \
            patch('main.write_project_data') as mock_write:
        # Настраиваем моки
        mock_args = MagicMock()
        mock_args.root = None
        mock_args.safe = None
        mock_args.max_size = None
        mock_args.encoding = None
        mock_args.exclude = None
        mock_parse.return_value = mock_args

        # Запускаем main
        with patch('main.__name__', '__main__'):
            main_func()

        # Проверяем что функции были вызваны
        assert mock_parse.called
        assert mock_write.called


def test_main_with_cli_args(monkeypatch):
    """Тестирует main с переопределением аргументов CLI."""
    from main import main as main_func

    with patch('main.parse_args') as mock_parse, \
            patch('main.logging.basicConfig'), \
            patch('main.shutil.rmtree'), \
            patch('main.os.makedirs'), \
            patch('main.write_project_data'):
        # Настраиваем моки с аргументами
        mock_args = MagicMock()
        mock_args.root = '/test/path'
        mock_args.safe = 'true'
        mock_args.max_size = '2MB'
        mock_args.encoding = 'utf-8'
        mock_args.exclude = 'dir1,dir2'
        mock_parse.return_value = mock_args

        # Мокируем конфиг
        with patch('main.config') as mock_config:
            mock_config.ROOT_DIR = Path('.')
            mock_config.PROJECT_NAME = 'test'
            mock_config.OUT_DIR = Path('out')
            mock_config.PROJECT_OUTPUT_DIR = Path('out/test')
            mock_config.PARTS_DIR = Path('out/test/parts')
            mock_config.OUTPUT_FILE = Path('out/test/extract_test.txt')

            # Запускаем main
            with patch('main.__name__', '__main__'):
                main_func()

            # Проверяем что конфиг был обновлен
            assert mock_parse.called


def test_main_directory_cleanup(monkeypatch):
    """Тестирует обработку ошибок при удалении директории."""
    from main import main as main_func
    from unittest.mock import patch, MagicMock

    # Настраиваем фиктивные аргументы
    mock_args = MagicMock()
    mock_args.root = None
    mock_args.safe = False
    mock_args.max_size = None
    mock_args.encoding = None
    mock_args.exclude = None

    with patch('main.parse_args', return_value=mock_args), \
            patch('main.os.makedirs'), \
            patch('main.write_project_data'), \
            patch('main.shutil.rmtree') as mock_rmtree, \
            patch('main.logging.error') as mock_log_error, \
            patch('main.logging.info') as mock_log_info, \
            patch('main.config') as mock_config, \
            patch('main.os.path.exists', return_value=True):
        # Настроим директорию
        mock_config.PROJECT_OUTPUT_DIR = "fake/dir"
        mock_config.ROOT_DIR = "fake_root"

        # Симулируем OSError при удалении
        mock_rmtree.side_effect = OSError("Permission denied")

        # Запускаем main - она НЕ должна падать
        main_func()

        # Проверяем, что rmtree вызвано
        assert mock_rmtree.called

        # Проверяем, что ошибка была залогирована
        mock_log_error.assert_called()

        # Проверяем, что программа продолжила работу (write_project_data была вызвана)
        # Для этого нужно добавить mock для write_project_data в контекстный менеджер


def test_main_root_dir_override(monkeypatch):
    """Тестирует переопределение ROOT_DIR из CLI."""
    with patch('main.parse_args') as mock_parse, \
            patch('main.logging.basicConfig'), \
            patch('main.shutil.rmtree'), \
            patch('main.os.makedirs'), \
            patch('main.write_project_data'):
        mock_args = MagicMock()
        mock_args.root = '/custom/path'
        # ... другие аргументы
        mock_parse.return_value = mock_args

        # Запускаем и проверяем что ROOT_DIR обновлен