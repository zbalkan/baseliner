import os
import subprocess
from dataclasses import dataclass
from typing import Optional

ARF_PATH: str = "/tmp/arf.xml"
ENCODING: str = "utf-8"


@dataclass
class StigScap:

    @staticmethod
    def generate_ansible(profileId: str, outputDirectory: str, tmpXmlFile: str) -> None:
        ansiblePath: str = os.path.join(outputDirectory, f"{profileId}.yml")
        sanitizedProfileId: str = profileId.replace(" ", "_")

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitizedProfileId} --results-arf {ARF_PATH} {tmpXmlFile}")

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {tmpXmlFile} > {tmpXmlFile}.new")

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {tmpXmlFile}; mv {tmpXmlFile}.new {tmpXmlFile}")

        # Generate ansible script
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf generate fix --fetch-remote-resources --fix-type ansible --result-id \"\" {ARF_PATH} > {ansiblePath}")

        os.remove(ARF_PATH)

    @staticmethod
    def generate_audit_report(profileId: str, outputDirectory: str, tmpXmlFile: str) -> None:
        reportPath: str = os.path.join(outputDirectory, f"{profileId}.html")
        sanitizedProfileId: str = profileId.replace(" ", "_")

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitizedProfileId} --results-arf {ARF_PATH} {tmpXmlFile}")

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {tmpXmlFile} > {tmpXmlFile}.new")

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {tmpXmlFile}; mv {tmpXmlFile}.new {tmpXmlFile}")

        # Generate audit report
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitizedProfileId} --results-arf {ARF_PATH} --report {reportPath}.html {tmpXmlFile}")

        os.remove(ARF_PATH)

    @ staticmethod
    def __run_oscap_command(command: str) -> None:
        output: Optional[bytes] = None
        try:
            output = subprocess.check_output(command.split(" "))
        except Exception as ex:
            StigScap.__raise_command_exception(output=output, ex=ex)

    @ staticmethod
    def __raise_command_exception(output: Optional[bytes], ex: Exception) -> None:
        if (output):
            err: str = bytes.decode(output, ENCODING)
            raise Exception(
                f"Command failed:\n{err}", str(ex))
        else:
            raise Exception(
                f"Command failed.", str(ex))
