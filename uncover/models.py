import typing as t
import zipfile
from io import BytesIO
from pathlib import Path

import xmltodict
from PIL import Image

import dataclasses


@dataclasses.dataclass
class Epub:
    file_path: Path
    _manifest: object = None
    _archive: zipfile.ZipFile = None

    @property
    def archive(self):
        if self._archive is None:
            self._archive = zipfile.ZipFile(self.file_path, "r")
        return self._archive

    @property
    def manifest(self):
        if self._manifest is None:
            self._manifest = xmltodict.parse(
                self.archive.read("META-INF/container.xml")
            )
        return self._manifest

    @property
    def filelist(self):
        return self.archive.namelist()

    @property
    def cover_candidates(self):
        return self.cover_from_manifest() + self.cover_from_files()

    @property
    def best(self):
        return self.cover_candidates[0]

    @property
    def cover(self):
        return self.archive.read(self.best)

    def cover_from_manifest(self):
        return []

    def cover_from_files(self):
        return [f for f in self.filelist if "cover" in f]

    def write_thumbnail(self, out_file: Path, size: int):
        image = Image.open(BytesIO(self.cover))
        image.thumbnail((size, size), Image.ANTIALIAS)
        if image.mode == "CMYK":
            image = image.convert("RGB")
        image.save(out_file, "PNG")
        return "wrote image"


class Lit:
    pass


class Mobi:
    pass
