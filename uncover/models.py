import typing as t
import zipfile
from pathlib import Path

import xmltodict
from PIL import Image

import dataclasses


class Ebook:
    cover_file: t.Any = None

    def output_thumbnail(self, out_file: Path, size: int):
        image = Image.open(self.cover_file)
        image.thumbnail((size, size), Image.ANTIALIAS)
        if image.mode == "CMYK":
            image = image.convert("RGB")
        image.save(out_file, "PNG")


@dataclasses.dataclass
class Epub(Ebook):
    file_path: Path
    manifest: object = None

    @property
    def manifest(self):
        if self.manifest is None:
            archive = zipfile.ZipFile(self.file_path, "r")
            self.manifest = xmltodict.parse(archive.read("META-INF/container.xml"))
        return self.manifest


class Lit:
    pass


class Mobi:
    pass
