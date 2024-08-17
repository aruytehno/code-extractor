import os
import fnmatch

def write_code_to_file(root_dir, output_file, exclude_dirs, file_types):
    """
    Записывает содержимое файлов определенных типов в текстовый файл.

    :param root_dir: Корневая директория проекта.
    :param output_file: Имя файла, в который будет записан весь код.
    :param exclude_dirs: Множество директорий, которые необходимо исключить из обхода.
    :param file_types: Список типов файлов (например, ['*.py', '*.js']), содержимое которых нужно записать.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for root, dirs, files in os.walk(root_dir):
            # Пропускаем исключённые директории
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                if any(fnmatch.fnmatch(file, pattern) for pattern in file_types):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as code_file:
                        f.write(f'-- File: {file_path} --\n')
                        f.write(code_file.read())
                        f.write('\n\n')  # Разделение между файлами

def write_project_structure(root_dir, output_file, exclude_dirs, file_types):
    """
    Записывает структуру проекта в текстовый файл, включая только директории с файлами определенных типов.

    :param root_dir: Корневая директория проекта.
    :param output_file: Имя файла, в который будет записана структура проекта.
    :param exclude_dirs: Множество директорий, которые необходимо исключить из обхода.
    :param file_types: Список типов файлов (например, ['*.py', '*.js']), наличие которых определяет, будет ли директория включена в структуру.
    """
    with open(output_file, 'a', encoding='utf-8') as f:
        # Записываем корневую директорию проекта
        f.write(f'{os.path.basename(root_dir)}/\n')

        for root, dirs, files in os.walk(root_dir):
            # Пропускаем исключённые директории
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            # Проверяем, есть ли в текущем каталоге файлы с нужными расширениями
            if any(any(fnmatch.fnmatch(file, pattern) for pattern in file_types) for file in files):
                level = root.replace(root_dir, '').count(os.sep)
                indent = '│   ' * level + '├── '
                f.write(f'{indent}{os.path.basename(root)}/\n')

                subindent = '│   ' * (level + 1)
                for file in files:
                    if any(fnmatch.fnmatch(file, pattern) for pattern in file_types):
                        f.write(f'{subindent}├── {file}\n')

if __name__ == "__main__":
    project_root = '/Users/aruytehno/PycharmProjects/med_service'  # Корневая директория проекта
    output_file = 'all_code.txt'
    exclude_dirs = {'node_modules', 'venv', 'gpt-prompts'}
    file_types = ['*.py', '*.js']

    # Записываем код всех файлов определенных типов в файл
    write_code_to_file(project_root, output_file, exclude_dirs, file_types)

    # Записываем структуру проекта в файл
    write_project_structure(project_root, output_file, exclude_dirs, file_types)

    print(f'Код всех {", ".join(file_types)} файлов и структура проекта записаны в {output_file}.')
