import os
from dataclasses import dataclass
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
    def generate_stig_zip(zip_file_path: str, output_directory: str, folder_in_zip: str, xccdf_file_in_zip: str, modified_xccdf: str) -> None:
        zin: ZipFile = ZipFile(zip_file_path, 'r')
        zout: ZipFile = ZipFile(os.path.join(
            output_directory, os.path.basename(zip_file_path).replace(".zip", "_new.zip")), 'w')
        for item in zin.infolist():
            buffer: bytes = zin.read(item.filename)
            if (item.filename.find(xccdf_file_in_zip) == -1):
                zout.writestr(item, buffer)
        zout.write(modified_xccdf, f"{folder_in_zip}/{xccdf_file_in_zip}")
        zout.close()
        zin.close()
