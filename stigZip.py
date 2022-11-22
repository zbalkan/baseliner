import os
from dataclasses import dataclass
from zipfile import ZipFile

ENCODING: str = "utf-8"


@dataclass
class StigZip:

    @staticmethod
    def read_xccdf(zipFilePath: str) -> bytes:
        archive: ZipFile = ZipFile(zipFilePath, 'r')
        baseFileName: str = os.path.basename(zipFilePath)
        folderName: str = baseFileName.replace(
            "_STIG", "_Manual_STIG").removesuffix(".zip")
        xccdfFileName: str = folderName.replace(
            "_STIG", "-xccdf.xml").replace("_V1R6", "_STIG_V1R6")
        fileAsBytes: bytes = archive.read(f"{folderName}/{xccdfFileName}")
        archive.close()
        return fileAsBytes

    @staticmethod
    def extract_xccdf(zipFilePath: str, output: str) -> tuple[str, str]:
        archive: ZipFile = ZipFile(zipFilePath, 'r')
        baseFileName: str = os.path.basename(zipFilePath)
        folderName: str = baseFileName.replace(
            "_STIG", "_Manual_STIG").removesuffix(".zip")
        xccdfFileName: str = folderName.replace(
            "_STIG", "-xccdf.xml").replace("_V1R6", "_STIG_V1R6")
        archive.extract(f"{folderName}/{xccdfFileName}", output)
        archive.close()
        return folderName, xccdfFileName

    @staticmethod
    def generate_stig_zip(zipFilePath: str, outputDirectory: str, folderInZip: str, xccdfFileInZip: str, modifiedXccdf: str) -> None:
        zin: ZipFile = ZipFile(zipFilePath, 'r')
        zout: ZipFile = ZipFile(os.path.join(
            outputDirectory, os.path.basename(zipFilePath).replace(".zip", "_new.zip")), 'w')
        for item in zin.infolist():
            buffer: bytes = zin.read(item.filename)
            if (item.filename.find(xccdfFileInZip) == -1):
                zout.writestr(item, buffer)
        zout.write(modifiedXccdf, f"{folderInZip}/{xccdfFileInZip}")
        zout.close()
        zin.close()
