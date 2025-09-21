from unittest.mock import patch
from cli import parse_args, parse_size


def test_parse_args():
    """Тестирует разбор аргументов командной строки."""
    test_args = [
        '--root', '/test/path',
        '--safe', 'false',
        '--max-size', '2MB',
        '--encoding', 'cp1251',
        '--exclude', 'dir1,dir2'
    ]

    with patch('sys.argv', ['cli.py'] + test_args):
        args = parse_args()

        assert args.root == '/test/path'
        assert args.safe == 'false'
        assert args.max_size == '2MB'
        assert args.encoding == 'cp1251'
        assert args.exclude == 'dir1,dir2'


def test_parse_size():
    """Тестирует парсинг размеров файлов."""
    assert parse_size('1024') == 1024
    assert parse_size('2KB') == 2048
    assert parse_size('1MB') == 1048576
    assert parse_size('500B') == 500
    assert parse_size('0') == 0