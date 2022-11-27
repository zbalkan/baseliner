import glob
import os
import re
import xml.etree.ElementTree as ET
from typing import Optional

import ruamel.yaml
from stigOs import StigOs

from stigZip import StigZip

ENCODING: str = "utf-8"


class StigAnsible:

    loader: ruamel.yaml.YAML
    dumper: ruamel.yaml.YAML

    def __init__(self) -> None:
        self.loader = self.__get_loader()
        self.dumper = self.__get_dumper()

    def cleanup(self, output_directory: str) -> None:
        StigOs.remove_with_pattern(output_directory=output_directory,
                                   pattern="*-ansible.zip")

    def generate_ansible(self, ansible_zip: str, output_directory: str) -> None:
        data_in: list = self.load_from_zip(
            ansible_zip, output_directory)

        denylist: list[str] = self.__generate_denylist(output_directory)

        data_out: list = self.filter_denied(
            data_in=data_in, denylist=denylist)

        export_path: str = os.path.join(
            output_directory, "custom.tasks.main.yml")
        self.dump(path=export_path, data_out=data_out)

    def load_from_file(self, path: str) -> list:
        with open(path, 'r', encoding=ENCODING) as file:
            text: str = file.read()
            return self.load_from_str(text=text)

    def load_from_zip(self, ansible_zip: str, output_directory: str) -> list:
        extractedfile: Optional[str] = StigZip.extract_ansible_zip(zip_file_path=ansible_zip,
                                                                   output_directory=output_directory)
        if (extractedfile is None):
            raise Exception("Ansible zip file could not be found.")

        tasks: str = bytes.decode(StigZip.read_ansible_tasks(
            os.path.join(output_directory, extractedfile)), encoding=ENCODING)

        return self.load_from_str(tasks)

    def load_from_str(self, text: str) -> list:
        def __handle_exclamation_mark(text: str) -> str:

            before: list = re.findall(r"(! systemctl.*)$", text, re.MULTILINE)

            pattern: str = r"(! systemctl.*)$"
            replacement: str = r"'\1'"
            modified: str = re.sub(pattern, replacement,
                                   text, flags=re.MULTILINE)

            after: list = re.findall(
                r"'! systemctl.*'$", modified, re.MULTILINE)

            if (len(before) != len(after)):
                raise Exception("Parsing error.")

            return modified

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

    def __generate_denylist(self, output_directory: str) -> list[str]:
        denylist: list[str] = []

        tree: ET.ElementTree = ET.parse(
            os.path.join(output_directory, "rationale.xml"))
        root: ET.Element = tree.getroot()
        for child in root:
            rule: Optional[str] = child.attrib.get("rule")
            if (rule):
                denylist.append(rule.replace("V-", ""))
        return denylist
