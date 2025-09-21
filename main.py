# main.py

import logging
import os
import shutil
import config
from extractor import write_project_data
from cli import parse_args, parse_size

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    args = parse_args()

    # Переопределяем конфигурацию из CLI, если есть
    if args.root:
        config.ROOT_DIR = os.path.normpath(args.root)
        config.PROJECT_NAME = os.path.basename(config.ROOT_DIR)
        config.PROJECT_OUTPUT_DIR = os.path.join(config.OUT_DIR, config.PROJECT_NAME)
        config.PARTS_DIR = os.path.join(config.PROJECT_OUTPUT_DIR, "parts")
        config.OUTPUT_FILE = os.path.join(config.PROJECT_OUTPUT_DIR, f"extract_{config.PROJECT_NAME}.txt")

    if args.safe:
        config.SAFE_MODE = args.safe.lower() == "true"

    if args.max_size:
        config.MAX_FILE_SIZE = parse_size(args.max_size)

    if args.encoding:
        config.ENCODING = args.encoding

    if args.exclude:
        config.EXCLUDE_DIRS = set(args.exclude.split(","))

    # Готовим папки
    if os.path.exists(config.PROJECT_OUTPUT_DIR):
        try:
            shutil.rmtree(config.PROJECT_OUTPUT_DIR)
            rel_old_project_dir = os.path.relpath(config.PROJECT_OUTPUT_DIR, config.ROOT_DIR)
            logging.info(f"Старая папка проекта '{rel_old_project_dir}' удалена.")
        except OSError as e:
            rel_old_project_dir = os.path.relpath(config.PROJECT_OUTPUT_DIR, config.ROOT_DIR)
            logging.error(f"Не удалось удалить старую папку проекта '{rel_old_project_dir}': {e}")
            logging.info("Продолжаем работу с существующей папкой...")

    try:
        os.makedirs(config.PARTS_DIR, exist_ok=True)
        rel_project_dir = os.path.relpath(config.PROJECT_OUTPUT_DIR, config.ROOT_DIR)
        logging.info(f"Папка проекта '{rel_project_dir}' создана/готова.")
    except OSError as e:
        logging.error(f"Не удалось создать папку для результатов: {e}")
        logging.error("Программа не может продолжить работу.")
        return  # Завершаем выполнение, если нельзя создать папку

    # Запускаем экстракцию
    try:
        write_project_data()
        rel_output_file = os.path.relpath(config.OUTPUT_FILE, config.ROOT_DIR)
        logging.info(f"Структура и код сохранены в {rel_output_file}")
    except Exception as e:
        logging.error(f"Критическая ошибка во время экстракции: {e}")

if __name__ == "__main__":
    main()