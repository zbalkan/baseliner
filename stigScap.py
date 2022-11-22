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

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {fileName} --results-arf {ARF_PATH} {fileName}")

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {fileName} > {fileName}.new")

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {fileName}; mv {fileName}.new {fileName}")

        # Generate ansible script
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf generate fix --fetch-remote-resources --fix-type ansible --result-id \"\" {ARF_PATH} > {fullPath}.yml")

        os.remove(ARF_PATH)

    @staticmethod
    def generate_audit_report(customXccdf: str, outputDirectory: str, name: str = "custom") -> None:
        out: str = os.path.abspath(outputDirectory)
        fileName: str = name.replace(" ", "_")
        fullPath: str = os.path.join(out, fileName)

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {fileName} --results-arf {ARF_PATH} {fileName}")

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {customXccdf} > {fileName}.new")

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {fileName}; mv {fileName}.new {fileName}")

        # Generate audit report
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {fileName}--results-arf {ARF_PATH} --report {fullPath}.html {fileName}")

        os.remove(ARF_PATH)

    @staticmethod
    def __run_oscap_command(command: str) -> None:
        output: Optional[bytes] = None
        try:
            output = subprocess.check_output(command.split(" "))
        except Exception as ex:
            StigScap.__raise_command_exception(output=output, ex=ex)

    @staticmethod
    def __raise_command_exception(output: Optional[bytes], ex: Exception) -> None:
        if (output):
            err: str = bytes.decode(output, ENCODING)
            raise Exception(
                f"Command failed:\n{err}", str(ex))
        else:
            raise Exception(
                f"Command failed.", str(ex))
