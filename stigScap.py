import os
import subprocess
from dataclasses import dataclass
from typing import Optional

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
        StigScap.__run_oscap_command(command)

        command = f"sudo oscap xccdf generate fix --fetch-remote-resources --fix-type ansible --result-id \"\" {ARF_PATH} > {fullPath}.yml"
        StigScap.__run_oscap_command(command)

        os.remove(ARF_PATH)

    @staticmethod
    def generate_audit_report(customXccdf: str, outputDirectory: str, name: str = "custom") -> None:
        out: str = os.path.abspath(outputDirectory)
        fileName: str = name.replace(" ", "_")
        fullPath: str = os.path.join(out, fileName)
        command: str = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {ARF_PATH} {customXccdf}"
        StigScap.__run_oscap_command(command)

        command = f"sudo oscap xccdf eval --fetch-remote-resources --profile xccdf_org.ssgproject.content_profile_stig --results-arf {ARF_PATH} --report {fullPath}.html {customXccdf}"
        StigScap.__run_oscap_command(command)

        os.remove(ARF_PATH)

    @staticmethod
    def __run_oscap_command(command) -> None:
        output: Optional[bytes] = None
        try:
            output = subprocess.check_output(command.split(" "))
        except Exception as ex:
            StigScap.__raise_oscap_exception(output=output, ex=ex)

    @staticmethod
    def __raise_oscap_exception(output: Optional[bytes], ex: Exception) -> None:
        if (output):
            err: str = bytes.decode(output, ENCODING)
            raise Exception(
                f"Oscap failed:\n{err}", str(ex))
        else:
            raise Exception(
                f"Oscap failed.", str(ex))
