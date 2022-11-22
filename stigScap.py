import os
import subprocess
from dataclasses import dataclass

ARF_PATH: str = "/tmp/arf.xml"
ENCODING: str = "utf-8"


@dataclass
class StigScap:

    @staticmethod
    def generate_ansible(customXccdf: str, outputDirectory: str, name: str = "custom") -> None:
        out: str = os.path.abspath(outputDirectory)
        fileName: str = name.replace(" ", "_")
        fullPath: str = os.path.join(out, fileName)
        command: str = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {ARF_PATH} {customXccdf}"
        try:
            _: bytes = subprocess.check_output(command.split(" "))
        except Exception as ex:
            raise Exception("Oscap failed", str(ex))
        command = f"sudo oscap xccdf generate fix --fetch-remote-resources --fix-type ansible --result-id \"\" {ARF_PATH} > {fullPath}.yml"
        try:
            _: bytes = subprocess.check_output(command.split(" "))
        except Exception as ex:
            raise Exception("Oscap failed", str(ex))
        os.remove(ARF_PATH)

    @staticmethod
    def generate_audit_report(customXccdf: str, outputDirectory: str, name: str = "custom") -> None:
        out: str = os.path.abspath(outputDirectory)
        fileName: str = name.replace(" ", "_")
        fullPath: str = os.path.join(out, fileName)
        command: str = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {ARF_PATH} {customXccdf}"
        try:
            _: bytes = subprocess.check_output(command.split(" "))
        except Exception as ex:
            raise Exception("Oscap failed", str(ex))
        command = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {ARF_PATH} --report {fullPath}.html {customXccdf}"
        try:
            _: bytes = subprocess.check_output(command.split(" "))
        except Exception as ex:
            raise Exception("Oscap failed", str(ex))
        os.remove(ARF_PATH)
