import os
import re
import sys
import xml.etree.ElementTree as ET

from colorama import Fore, Style

from stigParser import Benchmark, Group, Preference, Profile, Select
from stigScap import StigScap
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
                match = re.search("profile:([0-9]+)", text)
                if match:
                    selected: int = int(match.group(1))
                    return benchmark.Profile[selected]
                else:
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

            return benchmark.Profile[selected]

    @staticmethod
    def filter_groups(benchmark: Benchmark, selectedProfile: Profile) -> list[Group]:
        rules: list[Group] = []
        for s in selectedProfile.select:
            for g in benchmark.Group:
                if (g.id == s.idref):
                    rules.append(g)
                    break
        return rules

    @staticmethod
    def prompt_preferences(selectedGroups: list[Group]) -> list[Preference]:
        scanPreferences: list[Preference] = []

        start: int = 0
        if (os.path.exists(CHECKPOINT_FILE)):
            with open(CHECKPOINT_FILE, "a+", encoding=ENCODING) as file:
                file.seek(0)
                text: str = file.read()

                match = re.search("last:([0-9]+)", text)
                if (match):
                    # Start after last saved answer, except it is already the beginning.
                    last: int = int(match.group(1))
                    if (last != 0):
                        start = last + 1
                else:
                    raise Exception(
                        "Invalid checkpoint file. Please remove the file and restart.")

        for i in range(start, len(selectedGroups), 1):
            group: Group = selectedGroups[i]
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
                    f"\n{line}\nDo you accept this rule for scan? ({i + 1}/{len(selectedGroups)}) [Y/n]: ")
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

            scanPreferences.append(preference)

            # Save as checkpoint
            with open(CHECKPOINT_FILE, "a+", encoding=ENCODING) as file:
                file.seek(0)
                content: str = file.read()
                content = re.sub(r"last:([0-9]+)", f"last:{i}", content)
                file.truncate(0)
                file.write(content)

        return scanPreferences

    @staticmethod
    def get_custom_profile(preferences: list[Preference]) -> Profile:
        selected: list[Select] = []

        accepted: list[Preference] = [
            p for p in preferences if p.applicable == True]
        for a in accepted:
            s: Select = Select(idref=a.id, selected="true")
            selected.append(s)

        customTitle: str = input("Title for you profile [Custom title]: ")
        if (customTitle == ""):
            customTitle = "Custom title"
        customDesc: str = input(
            "Description for your profile [Custom description]: ")
        if (customDesc == ""):
            customDesc = "Custom description"
        customId: str = customTitle.replace(" ", "_").replace("-", "_")
        custom: Profile = Profile(
            title=customTitle, description=customDesc, select=selected, id=customId)
        return custom

    @staticmethod
    def generate_profile(customProfile: Profile, stigFile: str, outputDirectory: str, tmpXmlFile: str) -> None:
        StigGenerator.__save_modified_zip(
            customProfile=customProfile, zipFilePath=stigFile, outputDirectory=outputDirectory, xmlOutput=tmpXmlFile)

    @staticmethod
    def generate_rationale(customProfile: Profile, preferences: list[Preference], outputDirectory: str) -> None:
        StigGenerator.__save_rationale_xml(
            profileName=customProfile.title, preferences=preferences, outputDirectory=outputDirectory)

    @staticmethod
    def generate_fix(customProfile: Profile, outputDirectory: str, tmpXmlFile: str) -> None:
        StigScap.generate_ansible(
            profileId=customProfile.id, outputDirectory=outputDirectory, tmpXmlFile=tmpXmlFile)

    @staticmethod
    def generate_report(customProfile: Profile, outputDirectory: str, tmpXmlFile: str) -> None:
        StigScap.generate_audit_report(
            profileId=customProfile.id, outputDirectory=outputDirectory, tmpXmlFile=tmpXmlFile)

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
    def __save_modified_zip(customProfile: Profile, zipFilePath: str, outputDirectory: str, xmlOutput: str) -> None:
        # Read from zip
        folderName, xccdfFileName = StigZip.extract_xccdf(
            zipFilePath=zipFilePath, outputDirectory=outputDirectory)

        # Create XML
        xmlInput: str = os.path.join(
            outputDirectory, f"{folderName}/{xccdfFileName}")
        StigGenerator.__generate_xml_file(
            customProfile=customProfile, originalXmlFile=xmlInput, generatedXmlFile=xmlOutput)

        # Create new zip

        StigZip.generate_stig_zip(zipFilePath=zipFilePath, outputDirectory=outputDirectory,
                                  folderInZip=folderName, xccdfFileInZip=xccdfFileName, modifiedXccdf=xmlOutput)

        # Cleanup
        # os.remove(xmlOutput)

    @staticmethod
    def __generate_xml_file(customProfile: Profile, originalXmlFile: str, generatedXmlFile: str) -> None:
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

        customProfileXml: ET.Element = StigGenerator.__generate_profile_xml(
            customProfile=customProfile)
        tree: ET.ElementTree = ET.parse(originalXmlFile)
        root: ET.Element = tree.getroot()
        index: int = StigGenerator.__get_profile_index(root=root)
        root.insert(index, customProfileXml)
        ET.indent(tree)

        tree.write(generatedXmlFile)

    @staticmethod
    def __save_rationale_xml(profileName: str, preferences: list[Preference], outputDirectory: str) -> None:
        rejected: list[Preference] = [
            p for p in preferences if p.applicable == False]

        attrs: dict = {}
        attrs["profile"] = profileName
        root: ET.Element = ET.Element("rationale", attrs)
        for r in rejected:
            attrs = {}
            attrs["rule"] = r.id
            attrs["title"] = r.rule
            attrs["rationale"] = r.rationale
            rationaleElement: ET.Element = ET.Element("item", attrs)
            root.append(rationaleElement)

        rationaleOutput: str = os.path.join(outputDirectory, "rationale.xml")
        with open(rationaleOutput, "w") as file:
            ET.indent(tree=root)
            xmlAsStr: str = ET.tostring(root, "unicode")
            file.write(xmlAsStr)

    @staticmethod
    def __generate_profile_xml(customProfile: Profile) -> ET.Element:
        id: dict = {}
        id["id"] = customProfile.id.replace(" ", "_")
        p: ET.Element = ET.Element("Profile", id)
        t: ET.Element = ET.SubElement(p, "title")
        t.text = customProfile.title
        d: ET.Element = ET.SubElement(p, "description")
        d.text = customProfile.description
        for s in customProfile.select:
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
    def __clear_unix() -> int: return os.system(command='clear')

    @staticmethod
    def __clear_win32() -> int: return os.system(command='cls')
