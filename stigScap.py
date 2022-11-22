import os
import stat
import subprocess
from dataclasses import dataclass
from typing import Optional

ARF_PATH: str = "/tmp/arf.xml"
ENCODING: str = "utf-8"


@dataclass
class StigScap:

    @staticmethod
    def generate_ansible(profile_id: str, output_directory: str, temp_xml_file: str) -> None:
        ansible_path: str = os.path.join(output_directory, f"{profile_id}.yml")
        sanitized_profile_id: str = profile_id.replace(" ", "_")

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitized_profile_id} --results-arf {ARF_PATH} {temp_xml_file}")

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {temp_xml_file} > {temp_xml_file}.new")

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {temp_xml_file}; mv {temp_xml_file}.new {temp_xml_file}")

        # Generate ansible script
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf generate fix --fetch-remote-resources --fix-type ansible --result-id \"\" {ARF_PATH} > {ansible_path}")

        os.remove(ARF_PATH)

    @staticmethod
    def generate_audit_report(profile_id: str, output_directory: str, temp_xml_file: str) -> None:
        report_path: str = os.path.join(output_directory, f"{profile_id}.html")
        sanitized_profile_id: str = profile_id.replace(" ", "_")

        # Create ARF result
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitized_profile_id} --results-arf {ARF_PATH} {temp_xml_file}")
        os.chmod(temp_xml_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH)

        # Convert XCCDF 1.1 to 1.2 for reports
        StigScap.__run_oscap_command(
            f" xsltproc --stringparam reverse_DNS org.open-scap xccdf_1.1_to_1.2.xsl {temp_xml_file} > {temp_xml_file}.new")
        os.chmod(f"{temp_xml_file}.new", stat.S_IRWXU |
                 stat.S_IRWXG | stat.S_IROTH)

        # Replace file
        StigScap.__run_oscap_command(
            f"rm {temp_xml_file}; mv {temp_xml_file}.new {temp_xml_file}")
        os.chmod(temp_xml_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH)

        # Generate audit report
        StigScap.__run_oscap_command(
            f"sudo oscap xccdf eval --fetch-remote-resources --profile {sanitized_profile_id} --results-arf {ARF_PATH} --report {report_path} {temp_xml_file}")
        os.chmod(f"{report_path}.html", stat.S_IRWXU |
                 stat.S_IRWXG | stat.S_IROTH)

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
