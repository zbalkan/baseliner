import os
from dataclasses import dataclass
from typing import Optional
from zipfile import ZipFile

ENCODING: str = "utf-8"


@dataclass
class StigZip:

    @staticmethod
    def read_xccdf(zip_file_path: str) -> bytes:
        archive: ZipFile = ZipFile(zip_file_path, 'r')
        base_file_name: str = os.path.basename(zip_file_path)
        folder_name: str = base_file_name.replace(
            "_STIG", "_Manual_STIG").removesuffix(".zip")
        xccdf_file_name: str = folder_name.replace(
            "_STIG", "-xccdf.xml").replace("_V1R6", "_STIG_V1R6")
        file_as_bytes: bytes = archive.read(f"{folder_name}/{xccdf_file_name}")
        archive.close()
        return file_as_bytes

    @staticmethod
    def extract_xccdf(zip_file_path: str, output_directory: str) -> tuple[str, str]:
        archive: ZipFile = ZipFile(zip_file_path, 'r')
        base_file_name: str = os.path.basename(zip_file_path)
        folder_name: str = base_file_name.replace(
            "_STIG", "_Manual_STIG").removesuffix(".zip")
        xccdf_file_name: str = folder_name.replace(
            "_STIG", "-xccdf.xml").replace("_V1R6", "_STIG_V1R6")
        archive.extract(f"{folder_name}/{xccdf_file_name}", output_directory)
        archive.close()
        return folder_name, xccdf_file_name

    @staticmethod
    def extract_ansible_zip(zip_file_path: str, output_directory: str) -> Optional[str]:
        archive: ZipFile = ZipFile(zip_file_path, 'r')
        extractedZip: Optional[str] = None
        for i, file in enumerate(archive.filelist):
            if (file.filename.endswith("ansible.zip")):
                extractedZip = file.filename
                archive.extract(member=extractedZip, path=output_directory)
        archive.close()
        return extractedZip

    @staticmethod
    def read_ansible_tasks(zip_file_path: str) -> bytes:
        archive: ZipFile = ZipFile(zip_file_path, 'r')
        base_file_name: str = os.path.basename(zip_file_path)
        folder_name: str = base_file_name.replace("-ansible.zip", "")
        file_as_bytes: bytes = archive.read(
            f"roles/{folder_name}/tasks/main.yml")
        archive.close()
        return file_as_bytes

    @staticmethod
    def generate_stig_zip(zip_file_path: str, output_directory: str, folder_in_zip: str, xccdf_file_in_zip: str, modified_xccdf: str) -> None:
        zin: ZipFile = ZipFile(zip_file_path, 'r')
        zout: ZipFile = ZipFile(os.path.join(
            output_directory, os.path.basename(zip_file_path).replace(".zip", "_custom.zip")), 'w')
        for item in zin.infolist():
            buffer: bytes = zin.read(item.filename)
            if (item.filename.find(xccdf_file_in_zip) == -1):
                zout.writestr(item, buffer)
        zout.write(modified_xccdf, f"{folder_in_zip}/{xccdf_file_in_zip}")
        zout.close()
        zin.close()
