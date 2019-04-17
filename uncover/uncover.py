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


import subprocess
import sys

from pathlib import Path
from xml.dom import minidom

import click
import xmltodict


valid_suffixes = ["epub"]
thumbnailer_source = Path(__file__).parents[0] / "epub.thumbnailer"
thumbnailer_target = Path("/usr/share/thumbnailers")


def gnome_info():
    gnome_version_xml_file = Path("/usr/share/gnome/gnome-version.xml")

    if not gnome_version_xml_file.is_file():
        return None
    else:
        with open(gnome_version_xml_file) as gcfg:
            config = xmltodict.parse(gcfg.read()).get("gnome-version", {})
        return {
            "platform": config.get("platform"),
            "distributor": config.get("distributor"),
        }


def docommand(command):
    click.echo("You may be prompted for sudo.")
    click.echo("Alternately, you can run this command yourself:")
    click.echo(" ".join(command))
    return subprocess.Popen(
        command, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.STDOUT
    )


def require_gnome_3():
    info = gnome_info()
    if int(info["platform"]) != 3:
        click.echo(f"Platform was not gnome 3: {info}")
        sys.exit(0)


def gnome_register():
    require_gnome_3()
    proc = docommand(["sudo", "cp", str(thumbnailer_source), str(thumbnailer_target)])
    proc.wait()

    if (thumbnailer_target / "epub.thumbnailer").is_file():
        click.echo(f"Thumbnailer has been registered with Gnome.")


def gnome_unregister():
    require_gnome_3()

    installed_thumbnailer = thumbnailer_target / "epub.thumbnailer"

    if not installed_thumbnailer.is_file():
        click.echo(f"{installed_thumbnailer} not found. Cannot unregister.")
    proc = docommand(["sudo", "rm", str(installed_thumbnailer)])
    proc.wait()


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
        if not source.is_file() and source.suffix in valid_suffixes:
            raise ValueError(
                f"{source.name} is not a valid instance of {valid_suffixes}"
            )
        get_thumbnail(in_file, out_file, size)
