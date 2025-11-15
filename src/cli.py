import argparse
import sys
import urllib.request
import json
import gzip

class DependencyVisualizer:
    def __init__(self):
        # ЭТАП 1
        self.params = self.parse_command_line()
        self.validate_params()

        # ЭТАП 2
        self.dependencies = self.get_dependencies()  # Этап 2
        self.print_dependencies()  # Этап 2

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

    def get_dependencies(self):                        # Получение прямых зависимостей пакета - ЭТАП 2
        package_name = self.params['package']
        version = self.params['version']
        repository_url = self.params['repository']

        print(f" Получение зависимостей для {package_name} версии {version}...")
        print(f" Репозиторий: {repository_url}")

        try:
            # Получаем данные о пакете из указанного репозитория
            package_data = self._fetch_package_data(package_name, repository_url)

            # Находим данные для нужной версии
            version_data = self._find_version_data(package_data, version)

            if not version_data:
                print(f" Версия {version} не найдена")
                return []

            # Извлекаем зависимости
            dependencies = self._extract_dependencies(version_data)
            return dependencies

        except Exception as e:
            print(f" Ошибка при получении зависимостей: {e}")
            return []

    def _fetch_package_data(self, package_name: str, repository_url: str) -> dict: # Получает данные о пакете из указанного репозитория
        api_url = f"{repository_url}/{package_name.lower()}/index.json"

        print(f" Запрос к: {api_url}")

        try:
            with urllib.request.urlopen(api_url) as response:
                # NuGet API возвращает gzip-сжатые данные
                compressed_data = response.read()

                # Распаковываем gzip
                decompressed_data = gzip.decompress(compressed_data)

                # Декодируем JSON
                return json.loads(decompressed_data.decode('utf-8'))

        except Exception as e:
            print(f" Ошибка при запросе к {api_url}: {e}")

    def _find_version_data(self, package_data: dict, target_version: str) -> dict: # Находит данные для конкретной версии пакета
        items = package_data.get('items', [])

        for item in items:
            for package in item.get('items', []):
                catalog_entry = package.get('catalogEntry', {})
                package_version = catalog_entry.get('version', '')

                if target_version == 'latest' or package_version == target_version:
                    return catalog_entry

        return {}

    def _extract_dependencies(self, version_data: dict) -> list:       # Извлекает список зависимостей из данных версии
        dependencies = []

        dependency_groups = version_data.get('dependencyGroups', [])

        for group in dependency_groups:
            for dependency in group.get('dependencies', []):
                dep_name = dependency.get('id', '')
                if dep_name:
                    dependencies.append(dep_name)

        return dependencies

    def print_dependencies(self): # Вывод прямых зависимостей
        if not self.dependencies:
            print("Зависимости не найдены")
            return

        print(f"\n=== Прямые зависимости пакета {self.params['package']} ===")
        for i, dep in enumerate(self.dependencies, 1):
            print(f"{i}. {dep}")
        print(f"Всего зависимостей: {len(self.dependencies)}")
        print("=============================================")


def main():
    try:
        visualizer = DependencyVisualizer()

    except Exception as e:
        print(f" Ошибка: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()