import glob
import os
import shutil
from dataclasses import dataclass

ENCODING: str = "utf-8"


@dataclass
class StigOs:

    @staticmethod
    def remove_with_pattern(output_directory: str, pattern: str) -> None:
        fileList: list[str] = glob.glob(
            os.path.join(output_directory, pattern))
        for filePath in fileList:
            try:
                os.remove(filePath)
            except:
                raise Exception("Error while deleting file : ", filePath)

    @staticmethod
    def remove_file(path: str) -> None:
        os.remove(path)

    @staticmethod
    def remove_dir(path: str) -> None:
        shutil.rmtree(path)
