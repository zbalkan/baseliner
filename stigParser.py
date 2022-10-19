from dataclasses import dataclass
from typing import Any, List, Optional


@dataclass
class Benchmark:
    Group: List['Group']
    Profile: List['Profile']
    description: str
    plain_text: List['PlainText']
    status: 'Status'
    title: str
    version: str

    @staticmethod
    def from_dict(obj: Any) -> 'Benchmark':
        _Group: list[Group] = [Group.from_dict(y) for y in obj.get("Group")]
        _Profile: list[Profile] = [
            Profile.from_dict(y) for y in obj.get("Profile")]
        _description: str = str(obj.get("description"))
        _plain_text: list[PlainText] = [
            PlainText.from_dict(y) for y in obj.get("plain-text")]
        _status: Status = Status.from_dict(obj.get("status"))
        _title: str = str(obj.get("title"))
        _version: str = str(obj.get("version"))
        return Benchmark(_Group, _Profile, _description, _plain_text, _status, _title, _version)


@dataclass
class Check:
    check_content: str

    @staticmethod
    def from_dict(obj: Any) -> 'Check':
        _check_content: str = str(obj.get("check-content"))
        return Check(_check_content)


@dataclass
class Fix:
    id: str

    @staticmethod
    def from_dict(obj: Any) -> 'Fix':
        _id: str = str(obj.get("@id"))
        return Fix(_id)


@dataclass
class Fixtext:
    text: str
    fixref: str

    @staticmethod
    def from_dict(obj: Any) -> 'Fixtext':
        _text: str = str(obj.get("#text"))
        _fixref: str = str(obj.get("@fixref"))
        return Fixtext(_text, _fixref)


@dataclass
class Group:
    id: str
    Rule: 'Rule'
    description: str
    title: str

    @staticmethod
    def from_dict(obj: Any) -> 'Group':
        _id: str = str(obj.get("@id"))
        _Rule: Rule = Rule.from_dict(obj.get("Rule"))
        _description: str = str(obj.get("description"))
        _title: str = str(obj.get("title"))
        return Group(_id, _Rule, _description, _title)


@dataclass
class PlainText:
    text: str
    id: str

    @staticmethod
    def from_dict(obj: Any) -> 'PlainText':
        _text: str = str(obj.get("#text"))
        _id: str = str(obj.get("@id"))
        return PlainText(_text, _id)


@dataclass
class Profile:
    id: str
    description: str
    select: List['Select']
    title: str

    @staticmethod
    def from_dict(obj: Any) -> 'Profile':
        _id: str = str(obj.get("@id"))
        _description: str = str(obj.get("description"))
        _select: list[Select] = [
            Select.from_dict(y) for y in obj.get("select")]
        _title: str = str(obj.get("title"))
        return Profile(_id, _description, _select, _title)


@dataclass
class Rule:
    id: str
    severity: str
    weight: str
    check: Check
    description: str
    fix: Fix
    fixtext: Fixtext
    title: str
    version: str

    @staticmethod
    def from_dict(obj: Any) -> 'Rule':
        _id: str = str(obj.get("@id"))
        _severity: str = str(obj.get("@severity"))
        _weight: str = str(obj.get("@weight"))
        _check: Check = Check.from_dict(obj.get("check"))
        _description: str = str(obj.get("description"))
        _fix: Fix = Fix.from_dict(obj.get("fix"))
        _fixtext: Fixtext = Fixtext.from_dict(obj.get("fixtext"))
        _title: str = str(obj.get("title"))
        _version: str = str(obj.get("version"))
        return Rule(_id, _severity, _weight, _check, _description, _fix, _fixtext, _title, _version)


@dataclass
class Select:
    idref: str
    selected: str

    @staticmethod
    def from_dict(obj: Any) -> 'Select':
        _idref: str = str(obj.get("@idref"))
        _selected: str = str(obj.get("@selected"))
        return Select(_idref, _selected)


@dataclass
class Status:
    text: str
    date: str

    @staticmethod
    def from_dict(obj: Any) -> 'Status':
        _text: str = str(obj.get("#text"))
        _date: str = str(obj.get("@date"))
        return Status(_text, _date)


@dataclass
class Preference:
    id: str
    rule: str
    applicable: bool
    rationale: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Preference':
        _id: str = str(obj.get("id"))
        _rule: str = str(obj.get("rule"))
        _rationale: str = str(obj.get("rationale"))
        _applicable: bool = bool(obj.get("applicable"))
        return Preference(_id, _rule, _applicable, _rationale)


@dataclass
class StigParser:
    Benchmark: Benchmark

    @staticmethod
    def from_dict(obj: Any) -> 'StigParser':
        _Benchmark: Benchmark = Benchmark.from_dict(obj.get("Benchmark"))
        return StigParser(_Benchmark)
