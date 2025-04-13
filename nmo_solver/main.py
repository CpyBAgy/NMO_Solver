"""
Main module for the NMO Solver application.
"""

import os
import time
import argparse

from nmo_solver import NmoParser


def run_console(parser):
    """
    Run the solver in console mode.

    Args:
        parser: NmoParser instance

    Returns:
        None
    """
    try:
        while True:
            target_url = input("Введите URL теста (или 'q' для выхода): ")
            if target_url.lower() in ('q', 'й'):
                break
            parser.solve(target_url)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
    finally:
        parser.close()


def run_file(parser):
    """
    Run the solver using URLs from a file.

    Args:
        parser: NmoParser instance

    Returns:
        None
    """
    try:
        urls_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "urls.txt")

        with open(urls_file) as f:
            urls = [url.strip() for url in f.readlines() if url.strip()]

        for url in urls:
            print(f"Обработка URL: {url}")
            parser.solve(url)
            time.sleep(10)

        print("Все тесты обработаны!")
    except FileNotFoundError:
        print("Файл urls.txt не найден. Создайте файл с URL тестов (по одному на строку).")
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
    finally:
        parser.close()


def main():
    """
    Main function to run the NMO Solver.

    Returns:
        None
    """
    parser = argparse.ArgumentParser(description="NMO Solver - автоматическое решение тестов на портале НМО")
    parser.add_argument("--file", action="store_true", help="Использовать URLs из файла urls.txt")
    parser.add_argument("--url", type=str, help="URL теста для решения")
    parser.add_argument("--username", type=str, help="СНИЛС для входа в формате '123-456-789 00'")
    parser.add_argument("--email", type=str, help="Email для входа (если используется)")
    parser.add_argument("--password", type=str, help="Пароль для входа")
    parser.add_argument("--profile", type=str, help="Путь к профилю Chrome")

    args = parser.parse_args()

    nmo_parser = NmoParser(
        username=args.username,
        email=args.email,
        password=args.password,
        path_to_profile=args.profile,
    )

    try:
        time.sleep(3)

        if args.url:
            nmo_parser.solve(args.url)
        elif args.file:
            run_file(nmo_parser)
        else:
            run_console(nmo_parser)
    except KeyboardInterrupt:
        print("\nПрограмма остановлена пользователем")
    finally:
        nmo_parser.close()


if __name__ == "__main__":
    main()