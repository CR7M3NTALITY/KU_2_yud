import argparse
import sys
import json
import urllib.request
from xml.etree import ElementTree as ET
from urllib.parse import urljoin


class DependencyVisualizer:
    def __init__(self):
        self.params = self.parse_command_line()
        self.validate_params()
        # Вывод параметров УДАЛЁН — он требуется ТОЛЬКО на Этапе 1

    def parse_command_line(self):
        parser = argparse.ArgumentParser(
            description='Инструмент визуализации графа зависимостей для менеджера пакетов .NET NuGet',
            epilog='Пример: python src/cli.py -p Newtonsoft.Json -r https://api.nuget.org/v3/index.json -v 13.0.3'
        )
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


class NuGetClient:
    def __init__(self, repository_url: str):
        self.repository_url = repository_url.rstrip('/')

    def _fetch_service_index(self):
        with urllib.request.urlopen(self.repository_url) as resp:
            index = json.load(resp)
        for resource in index.get('resources', []):
            if resource.get('@type') == 'PackageBaseAddress/3.0.0':
                return resource['@id']
        raise RuntimeError("PackageBaseAddress not found in service index")

    def get_package_dependencies(self, package_name: str, version: str):
        base_url = self._fetch_service_index()
        pkg_lower = package_name.lower()
        ver_lower = version.lower()
        nuspec_url = urljoin(base_url, f"{pkg_lower}/{ver_lower}/{pkg_lower}.nuspec")

        try:
            with urllib.request.urlopen(nuspec_url) as resp:
                nuspec_xml = resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise ValueError(f"Пакет '{package_name}' версии '{version}' не найден в репозитории.")
            raise

        root = ET.fromstring(nuspec_xml)
        ns = {'nuspec': 'http://schemas.microsoft.com/packaging/2013/05/nuspec.xsd'}

        # Ищем ВСЕ зависимости — даже внутри <group>
        dependencies = []
        for dep_elem in root.findall('.//nuspec:dependency', ns):
            dep_id = dep_elem.get('id')
            dep_version = dep_elem.get('version', '')
            if dep_id:  # только если id задан
                dependencies.append({'id': dep_id, 'version': dep_version})

        return dependencies


def main():
    try:
        visualizer = DependencyVisualizer()

        client = NuGetClient(visualizer.params['repository'])
        version = visualizer.params['version']

        deps = client.get_package_dependencies(
            package_name=visualizer.params['package'],
            version=version
        )

        if deps:
            for d in deps:
                print(f"{d['id']} ({d['version']})")
        else:
            print(f"Прямые зависимости для {visualizer.params['package']} версии {version} не найдены.")

    except Exception as e:
        print(f"Ошибка: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()