#!/usr/bin/python

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Author: Mariano Simone (http://marianosimone.com)
# Version: 1.0
# Name: epub-thumbnailer
# Description: An implementation of a cover thumbnailer for epub files
# Installation: see README

import os
import re
import zipfile
from io import BytesIO, StringIO
from pathlib import Path
from xml.dom import minidom

import click

try:
    from PIL import Image
except ImportError:
    import Image

img_ext_regex = re.compile(r"^.*\.(jpg|jpeg|png)$", flags=re.IGNORECASE)
cover_regex = re.compile(r".*cover.*\.(jpg|jpeg|png)", flags=re.IGNORECASE)


def get_cover_from_manifest(epub):

    # open the main container
    container = epub.open("META-INF/container.xml")
    container_root = minidom.parseString(container.read())

    # locate the rootfile
    elem = container_root.getElementsByTagName("rootfile")[0]
    rootfile_path = elem.getAttribute("full-path")

    # open the rootfile
    rootfile = epub.open(rootfile_path)
    rootfile_root = minidom.parseString(rootfile.read())

    # find possible cover in meta
    cover_id = None
    for meta in rootfile_root.getElementsByTagName("meta"):
        if meta.getAttribute("name") == "cover":
            cover_id = meta.getAttribute("content")
            break

    # find the manifest element
    manifest = rootfile_root.getElementsByTagName("manifest")[0]
    for item in manifest.getElementsByTagName("item"):
        item_id = item.getAttribute("id")
        item_properties = item.getAttribute("properties")
        item_href = item.getAttribute("href")
        item_href_is_image = img_ext_regex.match(item_href.lower())
        item_id_might_be_cover = item_id == cover_id or (
            "cover" in item_id and item_href_is_image
        )
        item_properties_might_be_cover = item_properties == cover_id or (
            "cover" in item_properties and item_href_is_image
        )
        if item_id_might_be_cover or item_properties_might_be_cover:
            return os.path.join(os.path.dirname(rootfile_path), item_href)

    return None


def get_cover_by_filename(epub):
    no_matching_images = []
    for fileinfo in epub.filelist:
        if cover_regex.match(fileinfo.filename):
            return fileinfo.filename
        if img_ext_regex.match(fileinfo.filename):
            no_matching_images.append(fileinfo)
    return _choose_best_image(no_matching_images)


def _choose_best_image(images):
    if images:
        return max(images, key=lambda f: f.file_size)
    return None


@click.command()
@click.argument("in_file")
@click.argument("out_file")
@click.option("--size", default=124, type=int, help="Output size.")
def get_thumbnail(in_file, out_file, size):
    file_path = Path(in_file)
    with file_path.open() as fp:
        # Unzip the epub
        epub = zipfile.ZipFile(file_path, "r")
    extraction_strategies = [get_cover_from_manifest, get_cover_by_filename]

    for strategy in extraction_strategies:
        try:
            cover_path = strategy(epub)
            if cover_path:
                cover = epub.open(cover_path)
                im = Image.open(BytesIO(cover.read()))
                im.thumbnail((size, size), Image.ANTIALIAS)
                if im.mode == "CMYK":
                    im = im.convert("RGB")
                im.save(out_file, "PNG")
                exit(0)
        except Exception as ex:
            print("Error getting cover using %s: " % strategy.__name__, ex)
