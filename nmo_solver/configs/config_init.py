"""
Module for initializing and managing configuration files.
"""

import shutil
import os
from pathlib import Path


def ensure_user_config():
    """
    Проверяет наличие файла user_config.py и создает его из шаблона,
    если файл отсутствует.

    Returns:
        bool: True if user config exists or was created successfully, False otherwise
    """
    current_dir = Path(__file__).parent
    user_config_path = current_dir / "user_config.py"
    example_config_path = current_dir / "user_config.py.example"

    if not user_config_path.exists() and example_config_path.exists():
        print("\nФайл user_config.py не найден. Создаем из шаблона...")
        shutil.copy(example_config_path, user_config_path)
        print(f"Создан файл {user_config_path}. Пожалуйста, отредактируйте его с вашими данными.")
        print("После редактирования перезапустите программу.\n")
        return False
    elif user_config_path.exists():
        from .user_config import USERNAME, PASSWORD, EMAIL, PATH_TO_CHROME_PROFILE
        if (USERNAME == "123-456-789 00" and EMAIL == "") or PASSWORD == "ваш_пароль" or PATH_TO_CHROME_PROFILE == "/path/to/chrome/profile":
            print("Пожалуйста, заполните USERNAME или EMAIL, PASSWORD и PATH_TO_CHROME_PROFILE в user_config.py.")
            return False

    return True


def ensure_answers_folder():
    """
    Create answers folder if it doesn't exist.

    Returns:
        str: Path to answers folder
    """
    package_dir = Path(__file__).parent
    answers_dir = package_dir.parent / "answers"

    os.makedirs(answers_dir, exist_ok=True)

    return str(answers_dir)


def ensure_certificates_folder():
    """
    Create certificates folder if it doesn't exist.

    Returns:
        str: Path to certificates folder
    """
    package_dir = Path(__file__).parent
    certificates_dir = package_dir.parent / "certificates"

    os.makedirs(certificates_dir, exist_ok=True)

    return str(certificates_dir)


if __name__ == "__main__":
    ensure_user_config()
    ensure_answers_folder()
    ensure_certificates_folder()