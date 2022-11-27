import os
import re
import stat
import sys
from typing import Optional
import xml.etree.ElementTree as ET

from colorama import Fore, Style

from stigParser import Benchmark, Group, Preference, Profile, Select
from stigZip import StigZip

CHECKPOINT_FILE: str = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "checkpoint.tmp")

ENCODING: str = "UTF-8"


class StigGenerator:

    @staticmethod
    def prompt_profile(benchmark: Benchmark) -> Profile:

        if (os.path.exists(CHECKPOINT_FILE)):
            with open(CHECKPOINT_FILE, "a+", encoding=ENCODING) as file:
                file.seek(0)
                text: str = file.read()
                match: Optional[re.Match[str]] = re.search(
                    "profile:([0-9]+)", text)  # type: ignore
                if match:
                    selected: int = int(match.group(1))
                    return benchmark.Profile[selected]

                raise Exception(
                    "Invalid checkpoint file. Please remove the file and restart.")
        else:
            StigGenerator.__clear_console()
            print(f"{Fore.GREEN}Please select a profile below:{Style.RESET_ALL}\n")
            opt: int = 1
            for profile in benchmark.Profile:
                print(f"[{opt}] {profile.title}")
                opt += 1

            selected = int(
                input(f"\n{Fore.GREEN}Selection: {Style.RESET_ALL}")) - 1

            # Save as checkpoint
            with open(CHECKPOINT_FILE, "a+", encoding=ENCODING) as file:
                file.write(f"profile:{selected}\nlast:0\n")
                os.chmod(CHECKPOINT_FILE, stat.S_IWRITE |
                         stat.S_IWGRP | stat.S_IROTH)

            return benchmark.Profile[selected]

    @staticmethod
    def filter_groups(benchmark: Benchmark, selected_profile: Profile) -> list[Group]:
        rules: list[Group] = []
        for s in selected_profile.select:
            for g in benchmark.Group:
                if (g.id == s.idref):
                    rules.append(g)
                    break
        return rules

    @staticmethod
    def prompt_preferences(selected_groups: list[Group]) -> list[Preference]:
        scan_preferences: list[Preference] = []

        start: int = 0
        if (os.path.exists(CHECKPOINT_FILE)):
            with open(CHECKPOINT_FILE, "a+", encoding=ENCODING) as file:
                file.seek(0)
                text: str = file.read()

                match: Optional[re.Match[str]] = re.search(
                    "last:([0-9]+)", text)
                if (match):
                    # Start after last saved answer, except it is already the beginning.
                    last: int = int(match.group(1))
                    if (last != 0):
                        start = last + 1
                else:
                    raise Exception(
                        "Invalid checkpoint file. Please remove the file and restart.")

        for i in range(start, len(selected_groups), 1):
            group: Group = selected_groups[i]
            preference: Preference = None  # type: ignore

            StigGenerator.__clear_console()
            print(
                f"{Fore.YELLOW}Title:{Style.RESET_ALL} {group.Rule.title}\n(severity: {Fore.RED}{group.Rule.severity}{Style.RESET_ALL}, weight: {Fore.RED}{group.Rule.weight}{Style.RESET_ALL})")

            # Fix new lines
            desc: str = group.Rule.description.replace("\\\\n", "\n")
            # Get rid of leftover XML tags
            desc = re.sub("</?[A-Za-z]+>", "", desc)
            print(
                f"\n{Fore.YELLOW}Description:{Style.RESET_ALL}\n{desc}")

            # Fix new lines
            mitigation: str = group.Rule.fixtext.text.replace("\\\\n", "\n")
            # Format code
            mitigation = re.sub(
                r"(\$.+)", fr"{Fore.GREEN}\1{Style.RESET_ALL}", mitigation)
            print(f"\n{Fore.YELLOW}Mitigation:{Style.RESET_ALL}\n{mitigation}")

            # Fix new lines
            control: str = group.Rule.check.check_content.replace(
                "\\\\n", "\n")
            # Format code
            control = re.sub(
                r"(\$.+)", fr"{Fore.GREEN}\1{Style.RESET_ALL}", control)
            print(
                f"\n{Fore.YELLOW}Control:{Style.RESET_ALL}\n{control}")

            invalid: bool = True
            prompt: str = ""
            while (invalid):
                size: int = os.get_terminal_size().columns
                line: str = ''.join(["*" for i in range(size)])
                prompt = input(
                    f"\n{line}\nDo you accept this rule for scan? ({i + 1}/{len(selected_groups)}) [Y/n]: ")
                if (prompt.capitalize() == "Y" or prompt.capitalize() == "N" or prompt == ""):
                    invalid = False

            if (prompt.capitalize() == "N"):
                invalid = True  # Do not accept empty description
                while (invalid):
                    rationale: str = input(
                        "Provide rationale on why you do not want to implement this measure (at least 3 chars): ")
                    if (len(rationale) >= 3):
                        preference = Preference(
                            id=group.id, rule=group.Rule.title, applicable=False, rationale=rationale)
                        invalid = False
            else:
                preference = Preference(
                    id=group.id, rule=group.Rule.title, applicable=True, rationale="")

            scan_preferences.append(preference)

            # Save as checkpoint
            with open(CHECKPOINT_FILE, "a+", encoding=ENCODING) as file:
                file.seek(0)
                content: str = file.read()
                content = re.sub(r"last:([0-9]+)", f"last:{i}", content)
                file.truncate(0)
                file.write(content)

        return scan_preferences

    @staticmethod
    def get_custom_profile(preferences: list[Preference]) -> Profile:
        selected: list[Select] = []

        accepted: list[Preference] = [
            p for p in preferences if p.applicable is True]
        for a in accepted:
            s: Select = Select(idref=a.id, selected="true")
            selected.append(s)

        custom_title: str = input("Title for you profile [Custom title]: ")
        if (custom_title == ""):
            custom_title = "Custom title"
        custom_description: str = input(
            "Description for your profile [Custom description]: ")
        if (custom_description == ""):
            custom_description = "Custom description"
        custom_id: str = custom_title.replace(" ", "_").replace("-", "_")
        custom_profile: Profile = Profile(
            title=custom_title, description=custom_description, select=selected, id=custom_id)
        return custom_profile

    @staticmethod
    def generate_profile(custom_profile: Profile, stig_file: str, output_directory: str, temp_xml_file: str) -> None:
        StigGenerator.__save_modified_zip(
            custom_profile=custom_profile, zip_file_path=stig_file, output_directory=output_directory, xml_output=temp_xml_file)

    @staticmethod
    def generate_rationale(custom_profile: Profile, preferences: list[Preference], output_directory: str) -> None:
        if (os.path.exists(os.path.join(output_directory, "rationale.xml"))):
            return
        StigGenerator.__save_rationale_xml(
            profile_name=custom_profile.title, preferences=preferences, output_directory=output_directory)

    @staticmethod
    def close() -> None:
        os.remove(CHECKPOINT_FILE)

    @staticmethod
    def __get_profile_index(root: ET.Element) -> int:
        for i in range(len(root)):
            child: ET.Element = root[i]
            if str(child.tag).endswith("Profile"):
                return i
        return -1

    @staticmethod
    def __save_modified_zip(custom_profile: Profile, zip_file_path: str, output_directory: str, xml_output: str) -> None:
        # Read from zip
        folder_name, xccdf_file_name = StigZip.extract_xccdf(
            zip_file_path=zip_file_path, output_directory=output_directory)

        # Create XML
        xml_input: str = os.path.join(
            output_directory, f"{folder_name}/{xccdf_file_name}")
        StigGenerator.__generate_xml_file(
            custom_profile=custom_profile, original_xml_file=xml_input, generated_xml_file=xml_output)

        # Create new zip

        StigZip.generate_stig_zip(zip_file_path=zip_file_path, output_directory=output_directory,
                                  folder_in_zip=folder_name, xccdf_file_in_zip=xccdf_file_name, modified_xccdf=xml_output)

        # Cleanup
        # os.remove(xmlOutput)

    @staticmethod
    def __generate_xml_file(custom_profile: Profile, original_xml_file: str, generated_xml_file: str) -> None:
        # DevSkim: ignore DS137138
        ET.register_namespace('', 'http://checklists.nist.gov/xccdf/1.1')
        # DevSkim: ignore DS137138
        ET.register_namespace('cpe', 'http://cpe.mitre.org/language/2.0')
        # DevSkim: ignore DS137138
        ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        # DevSkim: ignore DS137138
        ET.register_namespace('dsig', 'http://www.w3.org/2000/09/xmldsig#')
        # DevSkim: ignore DS137138
        ET.register_namespace('xhtml', 'http://www.w3.org/1999/xhtml')
        ET.register_namespace(
            'xsi', 'http://www.w3.org/2001/XMLSchema-instance')  # DevSkim: ignore DS137138

        custom_profile_xml: ET.Element = StigGenerator.__generate_profile_xml(
            custom_profile=custom_profile)
        tree: ET.ElementTree = ET.parse(original_xml_file)
        root: ET.Element = tree.getroot()
        index: int = StigGenerator.__get_profile_index(root=root)
        root.insert(index, custom_profile_xml)
        ET.indent(tree)

        tree.write(generated_xml_file)
        os.chmod(generated_xml_file, stat.S_IWRITE |
                 stat.S_IWGRP | stat.S_IROTH)

    @staticmethod
    def __save_rationale_xml(profile_name: str, preferences: list[Preference], output_directory: str) -> None:
        rejected: list[Preference] = [
            p for p in preferences if p.applicable is False]

        attrs: dict = {}
        attrs["profile"] = profile_name
        root: ET.Element = ET.Element("rationale", attrs)
        for r in rejected:
            attrs = {}
            attrs["rule"] = r.id
            attrs["title"] = r.rule
            attrs["rationale"] = r.rationale
            rationale_element: ET.Element = ET.Element("item", attrs)
            root.append(rationale_element)

        rationale_output: str = os.path.join(output_directory, "rationale.xml")
        with open(rationale_output, "w", encoding=ENCODING) as file:
            ET.indent(tree=root)
            xml_as_str: str = ET.tostring(root, "unicode")
            file.write(xml_as_str)
            os.chmod(rationale_output, stat.S_IWRITE |
                     stat.S_IWGRP | stat.S_IROTH)

    @staticmethod
    def __generate_profile_xml(custom_profile: Profile) -> ET.Element:
        id: dict = {}
        id["id"] = custom_profile.id.replace(" ", "_")
        p: ET.Element = ET.Element("Profile", id)
        t: ET.Element = ET.SubElement(p, "title")
        t.text = custom_profile.title
        d: ET.Element = ET.SubElement(p, "description")
        d.text = custom_profile.description
        for s in custom_profile.select:
            attr: dict = {}
            attr["idref"] = s.idref
            attr["selected"] = s.selected
            sel: ET.Element = ET.Element("select", attr)
            p.append(sel)
        ET.indent(p)
        return p

    @staticmethod
    def __clear_console() -> None:
        if (sys.platform == "win32"):
            _: int = StigGenerator.__clear_win32()
        else:
            _: int = StigGenerator.__clear_unix()

    @staticmethod
    def __clear_unix() -> int:
        return os.system(command='clear')

    @staticmethod
    def __clear_win32() -> int:
        return os.system(command='cls')
