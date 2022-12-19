#**********************************************************************
# Copyright 2020 Advanced Micro Devices, Inc
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#********************************************************************

import zipfile
import zlib
import os
import sys
import platform
from pathlib import Path
import subprocess
import shutil
import re
import argparse

OS = platform.system()
PYTHON_VERSION = f'{sys.version_info.major}.{sys.version_info.minor}'

repo_dir = Path(__file__).parent


def enumerate_addon_data(bin_dir):
    libs_rel_path = Path('libs/lib')
    plugin_rel_path = Path('libs/plugin/usd/plugin')
    plugin_path = bin_dir / 'USD/install/plugin'

    # copy addon scripts
    hydrarpr_plugin_dir = repo_dir / 'src/hydrarpr'
    for f in hydrarpr_plugin_dir.glob("**/*"):
        if f.is_dir():
            continue

        rel_path = f.relative_to(hydrarpr_plugin_dir)
        rel_path_parts = rel_path.parts
        if rel_path_parts[0] in ("libs", "configdev.py", "hdusd.log") or \
                "__pycache__" in rel_path_parts or ".gitignore" in rel_path_parts:
            continue

        yield f, rel_path

    hydrarpr_repo_dir = repo_dir / 'RadeonProRenderUSD'
    # copy legals and readmes
    for f in hydrarpr_repo_dir.glob("*"):
        if f.name in ("LICENSE.md", "README.md"):
            yield f, f.name

    # copy RIF libraries
    rif_libs_dir = hydrarpr_repo_dir / 'deps/RIF/Windows/Dynamic'
    for f in rif_libs_dir.glob("**/*"):
        if f.suffix in (".lib"):
            continue

        yield f, libs_rel_path / f.name
        
    # copy core libraries
    core_libs_dir = hydrarpr_repo_dir / 'deps/RPR/RadeonProRender/binWin64'
    for f in core_libs_dir.glob("**/*"):
        if f.suffix in (".exe"):
            continue

        yield f, libs_rel_path / f.name

    # copy rprUsd library
    rprusd_lib = hydrarpr_repo_dir / 'build/pxr/imaging/rprUsd/Release/rprUsd.dll'
    yield rprusd_lib, libs_rel_path / rprusd_lib.name

    # copy hdRpr library
    hdrpr_lib = hydrarpr_repo_dir / 'build/pxr/imaging/plugin/hdRpr/Release/hdRpr.dll'
    yield hdrpr_lib, plugin_rel_path.parent / hdrpr_lib.name

    # copy plugInfo.json library
    pluginfo = plugin_path / 'plugInfo.json'
    yield pluginfo, plugin_rel_path.parent.parent / pluginfo.name

    # copy plugin/usd folders
    for f in plugin_path.glob("**/*"):
        rel_path = f.relative_to(plugin_path.parent)
        if any(p in rel_path.parts for p in ("hdRpr", "rprUsd", 'rprUsdMetadata')):
            yield f, libs_rel_path.parent / rel_path


def get_version():
    return [1, 0, 0, 0]
    # getting buid version
    build_ver = subprocess.getoutput("git rev-parse --short HEAD")

    # getting plugin version
    text = (repo_dir / "src/hdusd/__init__.py").read_text()
    m = re.search(r'"version": \((\d+), (\d+), (\d+)\)', text)
    plugin_ver = m.group(1), m.group(2), m.group(3)

    return (*plugin_ver, build_ver)


def create_zip_addon(install_dir, bin_dir, name, ver):
    """ Pack addon files to zip archive """
    zip_addon = install_dir / name
    if zip_addon.is_file():
        os.remove(zip_addon)

    print(f"Compressing addon files to: {zip_addon}")
    with zipfile.ZipFile(zip_addon, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=zlib.Z_BEST_COMPRESSION) as myzip:
        for src, package_path in enumerate_addon_data(bin_dir):
            print(f"adding {src} --> {package_path}")

            arcname = str(Path('hydrarpr') / package_path)

            if str(package_path) == "__init__.py":
                print(f"    set version_build={ver[3]}")
                text = src.read_text()
                text = text.replace('version_build = ""', f'version_build = "{ver[3]}"')
                myzip.writestr(arcname, text)
                continue

            myzip.write(str(src), arcname=arcname)

    return zip_addon


def main(bin_dir):
    install_dir = repo_dir / "install"
    ver = get_version()
    name = f"hydrarpr-{ver[0]}.{ver[1]}.{ver[2]}-{ver[3]}-{OS.lower()}-{PYTHON_VERSION}.zip"

    if install_dir.is_dir():
        for file in os.listdir(install_dir):
            if file == name:
                os.remove(install_dir / file)
                break
    else:
        install_dir.mkdir()

    zip_addon = create_zip_addon(install_dir, bin_dir, name, ver)
    print(f"Addon was compressed to: {zip_addon}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()

    ap.add_argument("-bin-dir", required=False, type=str, default="",
                    help="Path to binary directory")

    args = ap.parse_args()

    bin_dir = Path(args.bin_dir).resolve() if args.bin_dir else (repo_dir / "bin")
    bin_dir = bin_dir.absolute()

    main(bin_dir)
