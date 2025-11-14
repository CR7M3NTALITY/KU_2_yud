import argparse
import sys


class DependencyVisualizer:
    def __init__(self):
        self.params = self.parse_command_line()
        self.validate_params()
        self.print_params()

    def parse_command_line(self):                    # Парсинг аргументов командной строки
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей для менеджера пакетов .NET NuGet',
            epilog='Пример: python src/cli.py -p Newtonsoft.Json -r https://api.nuget.org/v3/index.json'
        )

        # Все 8 параметров
        parser.add_argument('--package', '-p', required=True, help='Имя анализируемого пакета')
        parser.add_argument('--repository', '-r', required=True, help='URL репозитория или путь к тестовому файлу')
        parser.add_argument('--test-mode', '-t', action='store_true', help='Режим работы с тестовым репозиторием')
        parser.add_argument('--version', '-v', default='latest', help='Версия пакета')
        parser.add_argument('--output', '-o', default='graph.png', help='Имя файла с изображением графа')
        parser.add_argument('--ascii-tree', '-a', action='store_true', help='Вывод ASCII-дерева')
        parser.add_argument('--max-depth', '-d', type=int, default=10, help='Максимальная глубина анализа')
        parser.add_argument('--filter', '-f', default='', help='Подстрока для фильтрации пакетов')

        return vars(parser.parse_args())

    def validate_params(self):
    # Валидация параметров
        errors = []

        if not self.params['package'].strip():
            errors.append("Имя пакета не может быть пустым")

        if not self.params['repository'].strip():
            errors.append("URL репозитория не может быть пустым")

        if self.params['max_depth'] <= 0:
            errors.append("Максимальная глубина должна быть > 0")

        if errors:
            print("Ошибки валидации:")
            for error in errors:
                print(f"  - {error}")
            sys.exit(1)

    def print_params(self):
    # Вывод параметров в формате ключ-значение
        print("=== Параметры конфигурации ===")
        for key, value in self.params.items():
            print(f"{key}: {value}")
        print("==============================")


if __name__ == "__main__":
    try:
        visualizer = DependencyVisualizer()
        print(" Конфигурация успешно загружена!")
    except Exception as e:
        print(f" Ошибка: {e}")
        sys.exit(1)