import os
from dataclasses import dataclass
import subprocess


ENCODING: str = "utf-8"


@dataclass
class StigScap:

    @staticmethod
    def generate_ansible(customXccdf: str, outputDirectory: str, name: str = "custom") -> None:
        out: str = os.path.abspath(outputDirectory)
        fileName: str = name.replace(" ", "_")
        fullPath: str = os.path.join(out, fileName)
        arfPath: str = "/tmp/arf.xml"
        command: str = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {arfPath} {customXccdf}"
        subprocess.run(command.split(" "))
        command = f"sudo oscap xccdf generate fix --fetch-remote-resources --fix-type ansible --result-id \"\" {arfPath} > {fullPath}.yml"
        subprocess.run(command.split(" "))
        os.remove(arfPath)

    @staticmethod
    def generate_audit_report(customXccdf: str, outputDirectory: str, name: str = "custom") -> None:
        out: str = os.path.abspath(outputDirectory)
        fileName: str = name.replace(" ", "_")
        fullPath: str = os.path.join(out, fileName)
        arfPath: str = "/tmp/arf.xml"
        command: str = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {arfPath} {customXccdf}"
        subprocess.run(command.split(" "))
        command = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {arfPath} --report {fullPath}.html {customXccdf}"
        subprocess.run(command.split(" "))
        os.remove(arfPath)
