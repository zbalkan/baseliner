import xml.etree.ElementTree as ET

from stigParser import Benchmark, Group, Preference, Profile, Select


class StigGenerator:

    @staticmethod
    def prompt_profile(benchmark: Benchmark) -> Profile:
        print("Please select a profile below:\n")
        opt: int = 1
        for profile in benchmark.Profile:
            print(f"[{opt}] {profile.title}")
            opt += 1

        selected: str = input("\nSelection: ")
        return benchmark.Profile[int(selected) - 1]

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
        for i in range(len(selectedGroups)):
            group: Group = selectedGroups[i]
            preference: Preference = None  # type: ignore

            print(
                f"Title: {group.Rule.title} (severity: {group.Rule.severity}, weight: {group.Rule.weight})")
            print(f"Description: {group.Rule.description}")
            print(f"Mitigation: {group.Rule.fixtext}")
            print(f"Control: {group.Rule.check.check_content}")

            invalid: bool = True
            prompt: str = ""
            while (invalid):
                prompt = input(
                    f"Do you accept this rule for scan? ({i + 1}/{len(selectedGroups)}) [Y/n]: ")
                if (prompt.capitalize() == "Y" or prompt.capitalize() == "N" or prompt == ""):
                    invalid = False

            if (prompt.capitalize() == "N"):
                invalid = True  # Do not accept empty description
                while (invalid):
                    rationale: str = input(
                        "Provide rationale on why you do not want to implement this measure (at least 3 chars): ")
                    if (len(rationale) < 3):
                        preference = Preference(
                            group.id, group.Rule.title, False, rationale)
                        invalid = False
            else:
                preference = Preference(
                    group.id, group.Rule.title, True, "")

            scanPreferences.append(preference)

        return scanPreferences

    @staticmethod
    def get_custom_profile(preferences: list[Preference]) -> Profile:
        selected: list[Select] = []

        accepted: list[Preference] = [
            p for p in preferences if p.applicable == True]
        for a in accepted:
            s: Select = Select(a.id, "true")
            selected.append(s)

        customTitle: str = input("Title for you profile [Custom title]: ")
        if (customTitle == ""):
            customTitle = "Custom title"
        customDesc: str = input(
            "Description for your profile [Custom description]: ")
        if (customDesc == ""):
            customDesc = "Custom description"
        customId: str = customTitle.replace(" ", "_").replace("-", "_")
        custom: Profile = Profile(customTitle, customDesc, selected, customId)
        return custom

    @staticmethod
    def generate_profile(customProfile: Profile, input: str, output: str) -> None:
        customProfileXml: ET.Element = StigGenerator.__generate_profile_xml(
            customProfile)
        StigGenerator.__save_modified_xml(customProfileXml, input, output)

    @staticmethod
    def generate_rationale(customProfile: Profile, preferences: list[Preference], output: str) -> None:
        StigGenerator.__save_rationale_xml(
            customProfile.title, preferences, output)

    @staticmethod
    def get_profile_index(root: ET.Element) -> int:
        for i in range(len(root)):
            child: ET.Element = root[i]
            if str(child.tag).endswith("Profile"):
                return i
        return -1

    @staticmethod
    def __save_modified_xml(customProfileXml: ET.Element, input: str, output: str) -> None:
        ET.register_namespace('', 'http://checklists.nist.gov/xccdf/1.1')
        ET.register_namespace('cpe', 'http://cpe.mitre.org/language/2.0')
        ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
        ET.register_namespace('dsig', 'http://www.w3.org/2000/09/xmldsig#')
        ET.register_namespace('xhtml', 'http://www.w3.org/1999/xhtml')
        ET.register_namespace(
            'xsi', 'http://www.w3.org/2001/XMLSchema-instance')

        tree: ET.ElementTree = ET.parse(input)
        root: ET.Element = tree.getroot()
        index: int = StigGenerator.get_profile_index(root)
        root.insert(index, customProfileXml)
        ET.indent(tree)
        tree.write(output)

    @staticmethod
    def __save_rationale_xml(profileName: str, preferences: list[Preference], output: str) -> None:
        rejected: list[Preference] = [
            p for p in preferences if p.applicable == False]

        attrs: dict = {}
        attrs["profile"] = profileName
        root: ET.Element = ET.Element("rationale", attrib=attrs)
        for r in rejected:
            attrs: dict = {}
            attrs["rule"] = r.id
            attrs["title"] = r.rule
            attrs["rationale"] = r.rationale
            rationaleElement: ET.Element = ET.Element("item", attrs)
            root.append(rationaleElement)

        rationaleOutput: str = output.replace(".xml", ".rationale.xml")
        with open(rationaleOutput, "w") as file:
            ET.indent(root)
            xmlAsStr: str = ET.tostring(root, encoding="unicode")
            file.write(xmlAsStr)

    @staticmethod
    def __generate_profile_xml(custom: Profile) -> ET.Element:
        id: dict = {}
        id["id"] = custom.id.replace(" ", "_")
        p: ET.Element = ET.Element("Profile", id)
        t: ET.Element = ET.SubElement(p, "title")
        t.text = custom.title
        d: ET.Element = ET.SubElement(p, "description")
        d.text = custom.description
        for s in custom.select:
            attr: dict = {}
            attr["idref"] = s.idref
            attr["selected"] = s.selected
            sel: ET.Element = ET.Element("select", attr)
            p.append(sel)
        ET.indent(p)
        return p
