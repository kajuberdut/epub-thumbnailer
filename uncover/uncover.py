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
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path
from xml.dom import minidom

import click
from PIL import Image

valid_suffixes = ["epub"]

thumbnailer_file = """[Thumbnailer Entry]
Exec=uncover %u %o %s
MimeType=application/epub+zip
"""
thumbnailer_path = Path("/usr/share/thumbnailers")


def gnome_info():
    result_dict = {"platform": None, "distributor": None}
    gnome_version_xml_file = Path("/usr/share/gnome/gnome-version.xml")

    if not gnome_version_xml_file.isfile():
        return result_dict

    tree = ET.parse(gnome_version_xml_file)
    if tree.find("./platform"):
        result_dict["platform"] = tree.find("./platform").text
    if tree.find("./distributor"):
        result_dict["distributor"] = tree.find("./distributor").text
    return result_dict


def gnome_register():
    if not os.access(thumbnailer_path, os.W_OK):
        print(
            f"You do not have write permissions to {thumbnailer_path}. Try with sudo."
        )
        sys.exit(1)

    if gnome_info()["platform"] == 3:
        print(f"Installing thumbnailer hook in {thumbnailer_path} ...")
        Path(dst).mkdir(exist_ok=True, parents=True)
        with open(thumbnailer_path / "epub.thumbnailer", "w") as thumbnailer:
            thumbnailer.write(thumbnailer_file)
        print("registered")


def gnome_unregister():
    if gnome_info()["platform"] == 3:
        print(f"Uninstalling epub.thumbnailer from {thumbnailer_path} ...")
        (thumbnailer_path / "epub.thumbnailer").unlink()
        print("Unregistered")


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


def get_thumbnail(in_file, out_file, size):
    file_path = Path(in_file)
    # Unzip the epub
    epub = zipfile.ZipFile(file_path, "r")
    extraction_strategies = [get_cover_from_manifest, get_cover_by_filename]

    for strategy in extraction_strategies:
        try:
            cover_path = strategy(epub)
            if cover_path:
                cover = epub.open(cover_path)
                im = Image.open(cover.read())
                im.thumbnail((size, size), Image.ANTIALIAS)
                if im.mode == "CMYK":
                    im = im.convert("RGB")
                im.save(out_file, "PNG")
                exit(0)
        except Exception as ex:
            print("Error getting cover using %s: " % strategy.__name__, ex)


@click.command()
@click.argument("in_file", type=click.Path(), required=False)
@click.argument("out_file", type=click.Path(), required=False)
@click.option("--size", default=124, type=int, help="Output size.")
@click.option(
    "--register",
    default=False,
    type=bool,
    is_flag=True,
    help="Register thumbnailer with Nautilus.",
)
@click.option(
    "--unregister",
    default=False,
    type=bool,
    is_flag=True,
    help="Un-Register thumbnailer with Nautilus.",
)
def cli(in_file, out_file, size, register, unregister):
    if register:
        gnome_register()
    elif unregister:
        gnome_unregister()
    else:
        if not in_file:
            click.echo("No in/out files or other flag specified. See uncover --help.")
            sys.exit(0)
        else:
            source = Path(in_file)
        if not source.isfile() and source.suffix in valid_suffixes:
            raise ValueError(
                f"{source.name} is not a valid instance of {valid_suffixes}"
            )
        get_thumbnail(in_file, out_file, size)
