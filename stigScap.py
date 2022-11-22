import os
import subprocess
from dataclasses import dataclass
from typing import Optional

ARF_PATH: str = "/tmp/arf.xml"
ENCODING: str = "utf-8"


@dataclass
class StigScap:

    @staticmethod
    def generate_ansible(profileId: str, outputDirectory: str, benchmarkId: str) -> None:
        out: str = os.path.abspath(outputDirectory)
        sanitizedProfileId: str = profileId.replace(" ", "_")
        fullPath: str = os.path.join(out, benchmarkId, ".xml")

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitizedProfileId} --results-arf {ARF_PATH} {fullPath}")

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {fullPath} > {fullPath}.new")

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {fullPath}; mv {fullPath}.new {fullPath}")

        # Generate ansible script
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf generate fix --fetch-remote-resources --fix-type ansible --result-id \"\" {ARF_PATH} > {fullPath}.yml")

        os.remove(ARF_PATH)

    @staticmethod
    def generate_audit_report(profileId: str, outputDirectory: str, benchmarkId: str) -> None:
        out: str = os.path.abspath(outputDirectory)
        sanitizedProfileId: str = profileId.replace(" ", "_")
        fullPath: str = os.path.join(out, benchmarkId, ".xml")

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitizedProfileId} --results-arf {ARF_PATH} {fullPath}")

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {fullPath} > {fullPath}.new")

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {fullPath}; mv {fullPath}.new {fullPath}")

        # Generate audit report
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitizedProfileId} --results-arf {ARF_PATH} --report {fullPath}.html {fullPath}")

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
