import re
from typing import Optional

import ruamel.yaml

ENCODING: str = "utf-8"


class StigAnsible:

    loader: ruamel.yaml.YAML
    dumper: ruamel.yaml.YAML

    def __init__(self) -> None:
        self.loader = self.__get_loader()
        self.dumper = self.__get_dumper()

    def load(self, path: str) -> list:
        def __handle_exclamation_mark(text: str) -> str:

            before = re.findall(r"(! systemctl.*)$", text, re.MULTILINE)

            pattern = r"(! systemctl.*)$"
            replacement = r"'\1'"
            modified = re.sub(pattern, replacement, text, flags=re.MULTILINE)

            after = re.findall(r"'! systemctl.*'$", modified, re.MULTILINE)

            if (len(before) != len(after)):
                raise Exception("Parsing error.")

            return modified

        with open(path, 'r', encoding=ENCODING) as file:
            text: str = file.read()
            return self.loader.load(__handle_exclamation_mark(text=text))

    def dump(self, path: str, data_out: list) -> None:
        # Each task is a list item and requires offset of 0
        # But other list items need to be indented with an offset of 2
        # Solution is to indent first and strip later
        # ref: https://stackoverflow.com/questions/74551635/inconsistent-list-indent-in-ansible-yaml-file/
        def strip_first_two(text: str) -> str:
            res: list[str] = []
            for line in text.splitlines(True):
                stripped_line: str = line.lstrip()
                # do not dedent full comment lines
                if stripped_line and stripped_line[0] == '#' or not line.startswith('  '):
                    res.append(line)
                else:
                    res.append(line[2:])
            return ''.join(res)

        with open(path, "w", encoding=ENCODING) as file:
            self.dumper.dump(data_out, file, transform=strip_first_two)

    def filter_denied(self, data_in: list, denylist: list[str]) -> list:
        # Complexity O(m x n) where m: number of tasks and n: number of denied rules
        def __filter_out(elem: dict, denylist: list[str]) -> Optional[dict]:
            name: str = elem['name']
            pattern: re.Pattern[str] = re.compile(r"^stigrule_([0-9]+)_.*")
            match: re.Match[str] | None = pattern.match(name)
            if (match):
                number: str = match.group(1)
                for _, denied in enumerate(denylist):
                    if (denied == number):
                        return None

            return elem

        data_out: list = []

        for elem in data_in:
            if (__filter_out(elem, denylist) is not None):
                data_out.append(elem)

        return data_out

    def __get_loader(self) -> ruamel.yaml.YAML:
        yaml: ruamel.yaml.YAML = ruamel.yaml.YAML()
        yaml.default_flow_style = False
        yaml.preserve_quotes = True  # type: ignore
        yaml.width = 4096  # type: ignore # Prevent line breaks

        return yaml

    def __get_dumper(self) -> ruamel.yaml.YAML:
        yaml: ruamel.yaml.YAML = ruamel.yaml.YAML()
        yaml.default_flow_style = False
        yaml.preserve_quotes = True  # type: ignore
        yaml.width = 4096  # type: ignore # Prevent line breaks
        yaml.indent(mapping=2, sequence=4, offset=2)

        return yaml
