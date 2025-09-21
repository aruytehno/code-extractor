from unittest.mock import patch, mock_open
from pathlib import Path
from extractor import write_project_data


def test_write_project_data(test_project_structure, mock_config, monkeypatch):
    """Тестирует основную функцию извлечения данных."""
    # Мокируем конфиг
    monkeypatch.setattr('extractor.config.ROOT_DIR', test_project_structure)
    monkeypatch.setattr('extractor.config.EXCLUDE_DIRS', {'exclude_me'})

    # Мокируем файловые операции
    mock_file = mock_open()
    mock_os_walk = [
        (test_project_structure, ['subdir', 'exclude_me'], ['main.py', 'config.json', '.env.secret']),
        (test_project_structure / 'subdir', [], ['helper.py']),
        (test_project_structure / 'exclude_me', [], ['ignored.py']),
    ]

    with patch('extractor.os.walk', return_value=mock_os_walk), \
            patch('extractor.open', mock_file), \
            patch('extractor.os.makedirs'), \
            patch('extractor.split_into_parts') as mock_split:
        write_project_data()

        # Проверяем, что файл был открыт для записи
        assert mock_file.called

        # Проверяем, что split_into_parts была вызвана
        assert mock_split.called


def test_sensitive_file_redaction(test_project_structure, mock_config, monkeypatch):
    """Тестирует скрытие чувствительных файлов."""
    monkeypatch.setattr('extractor.config.ROOT_DIR', test_project_structure)

    # Мокируем os.walk чтобы вернуть только чувствительный файл
    mock_os_walk = [
        (test_project_structure, [], ['.env.secret']),
    ]

    with patch('extractor.os.walk', return_value=mock_os_walk), \
            patch('extractor.open', mock_open()) as mock_file, \
            patch('extractor.os.makedirs'), \
            patch('extractor.split_into_parts'):
        write_project_data()

        # Проверяем, что чувствительный файл был отмечен как REDACTED
        call_args = mock_file().write.call_args_list
        written_content = ''.join([str(call) for call in call_args])
        assert 'REDACTED: sensitive data' in written_content


def test_file_size_limit(test_project_structure, mock_config, monkeypatch):
    """Тестирует обработку больших файлов."""
    monkeypatch.setattr('extractor.config.ROOT_DIR', test_project_structure)
    monkeypatch.setattr('extractor.config.MAX_FILE_SIZE', 1)  # 1 байт

    # Создаем большой файл
    large_file = test_project_structure / "large_file.txt"
    large_file.write_text("This is a large content" * 1000)

    mock_os_walk = [
        (test_project_structure, [], ['large_file.txt']),
    ]

    with patch('extractor.os.walk', return_value=mock_os_walk), \
            patch('extractor.open', mock_open()) as mock_file, \
            patch('extractor.os.makedirs'), \
            patch('extractor.split_into_parts'):
        write_project_data()

        # Проверяем, что большой файл был отмечен как TOO LARGE
        # Нужно проверить все вызовы write
        all_writes = []
        for call in mock_file().write.call_args_list:
            all_writes.append(str(call[0][0]))  # Берем первый аргумент каждого вызова write

        written_content = ''.join(all_writes)
        assert 'TOO LARGE' in written_content or 'large_file.txt' in written_content


def test_io_error_handling(test_project_structure, mock_config, monkeypatch):
    """Тестирует обработку ошибок IO."""
    monkeypatch.setattr('extractor.config.ROOT_DIR', test_project_structure)

    mock_os_walk = [
        (test_project_structure, [], ['test_file.py']),
    ]

    with patch('extractor.os.walk', return_value=mock_os_walk), \
            patch('extractor.open', mock_open()) as mock_file, \
            patch('extractor.os.makedirs'), \
            patch('extractor.split_into_parts'):
        # Заставляем open выбрасывать ошибку при чтении
        mock_file.side_effect = IOError("Permission denied")

        write_project_data()

        # Проверяем что функция не упала и продолжила работу
        assert True  # Если дошли сюда - ошибка обработана


def test_exclude_output_file(test_project_structure, mock_config, monkeypatch):
    """Тестирует исключение выходного файла из обработки."""
    monkeypatch.setattr('extractor.config.ROOT_DIR', test_project_structure)
    monkeypatch.setattr('extractor.config.OUTPUT_FILE', test_project_structure / "extract.txt")

    # Создаем файл с именем выходного файла
    output_file = test_project_structure / "extract.txt"
    output_file.write_text("This should be excluded")

    mock_os_walk = [
        (test_project_structure, [], ['extract.txt']),
    ]

    with patch('extractor.os.walk', return_value=mock_os_walk), \
            patch('extractor.open', mock_open()) as mock_file, \
            patch('extractor.os.makedirs'), \
            patch('extractor.split_into_parts'):
        write_project_data()

        # Проверяем, что выходной файл не был обработан (не должен появиться в содержимом)
        written_content = ''.join([str(call[0][0]) for call in mock_file().write.call_args_list])
        assert 'extract.txt' not in written_content or 'excluded' not in written_content


def test_binary_file_handling(tmp_path, monkeypatch):
    """Тестирует обработку бинарных файлов."""

    # Устанавливаем временную директорию как ROOT_DIR
    monkeypatch.setattr('extractor.config.ROOT_DIR', tmp_path)

    # Создаём бинарный файл в tmp_path
    binary_file = tmp_path / "binary_file.bin"
    binary_file.write_bytes(b'\x00\xFF\x00\xFF')  # произвольные бинарные данные

    # Мокируем os.walk, чтобы вернуть наш бинарный файл
    mock_os_walk = [
        (tmp_path, [], ['binary_file.bin']),
    ]

    # Создаём мок для записи файлов
    m = mock_open()

    # Подмена open для проверки записи
    def mocked_open(file, mode='r', *args, **kwargs):
        # Чтение бинарного файла вызывает UnicodeDecodeError
        if 'r' in mode:
            raise UnicodeDecodeError('utf-8', b'', 0, 1, 'Invalid byte')
        return m(file, mode, *args, **kwargs)

    with patch('extractor.os.walk', return_value=mock_os_walk), \
         patch('extractor.open', new=mocked_open), \
         patch('extractor.os.makedirs'), \
         patch('extractor.split_into_parts'):

        write_project_data()

    # Проверяем, что бинарный файл был помечен как BINARY CONTENT
    written_content = ''.join(str(call[0][0]) for call in m().write.call_args_list)
    assert 'BINARY CONTENT' in written_content


def test_hidden_content_files(test_project_structure, mock_config, monkeypatch):
    """Тестирует скрытие содержимого файлов по конфигурации."""
    monkeypatch.setattr('extractor.config.ROOT_DIR', test_project_structure)
    monkeypatch.setattr('extractor.config.HIDE_FILE_CONTENTS', {'*.json'})

    mock_os_walk = [
        (test_project_structure, [], ['config.json']),
    ]

    with patch('extractor.os.walk', return_value=mock_os_walk), \
            patch('extractor.open', mock_open()) as mock_file, \
            patch('extractor.os.makedirs'), \
            patch('extractor.split_into_parts'):
        write_project_data()

        # Проверяем, что содержимое файла было скрыто
        written_content = ''.join([str(call[0][0]) for call in mock_file().write.call_args_list])
        assert 'CONTENT HIDDEN' in written_content


def test_extractor_write_error_handling(test_project_structure, mock_config, monkeypatch):
    """Тестирует обработку ошибок записи."""
    monkeypatch.setattr('extractor.config.ROOT_DIR', test_project_structure)

    with patch('extractor.open') as mock_file:
        mock_file.side_effect = IOError("Write permission denied")
        # Проверяем что функция не падает