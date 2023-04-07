# **********************************************************************
# Copyright 2022 Advanced Micro Devices, Inc
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
# ********************************************************************
import sys
from pathlib import Path
import subprocess
import os
import argparse
import platform
import shutil
import zipfile
import zlib
import os
import re

OS = platform.system()
repo_dir = Path(__file__).parent.resolve()


def rm_dir(d: Path):
    if not d.is_dir():
        return

    print(f"Removing: {d}")
    shutil.rmtree(str(d), ignore_errors=True)


def ch_dir(d: [Path, str]):
    print(f"Chdir: {d}")
    os.chdir(str(d))


def check_call(*args):
    args_str = " ".join((f'"{arg}"' if ' ' in arg else arg) for arg in (arg.replace('"', r'\"') for arg in args))
    print(f"Running: {args_str}")
    subprocess.check_call(args)


def copy(src: Path, dest, ignore=()):
    print(f"Copying: {src} -> {dest}")
    if src.is_dir():
        shutil.copytree(str(src), str(dest), ignore=shutil.ignore_patterns(*ignore), symlinks=True)
    else:
        shutil.copy(str(src), str(dest), follow_symlinks=False)


def print_start(msg):
    print(f"""
-------------------------------------------------------------
{msg}
-------------------------------------------------------------""")


def _cmake(d, compiler, jobs, build_var, args):
    cur_dir = os.getcwd()
    ch_dir(d)

    build_args = ['-B', 'build', *args]
    if compiler:
        build_args += ['-G', compiler]

    if build_var == 'relwithdebuginfo' and OS == 'Windows':
        # disabling optimization for debug purposes
        build_args.append(f'-DCMAKE_CXX_FLAGS_RELWITHDEBINFO=/Od')

    build_name = {'release': 'Release',
                  'debug': 'Debug',
                  'relwithdebuginfo': 'RelWithDebInfo'}[build_var]

    compile_args = [
        '--build', 'build',
        '--config', build_name,
        '--target', 'install'
    ]
    if jobs > 0:
        compile_args += ['--', '-j', str(jobs)]

    try:
        check_call('cmake', *build_args)
        check_call('cmake', *compile_args)

    finally:
        ch_dir(cur_dir)


def materialx(bin_dir, compiler, jobs, clean, build_var):
    materialx_dir = repo_dir / "MaterialX"

    if clean:
        rm_dir(materialx_dir / "build")

    _cmake(materialx_dir, compiler, jobs, build_var, [
        '-DMATERIALX_BUILD_SHARED_LIBS=ON',
        f'-DCMAKE_INSTALL_PREFIX={bin_dir / "USD/install"}',
    ])


def usd(bl_libs_dir, bin_dir, compiler, jobs, clean, build_var):
    print_start("Building USD")

    bl_libs_dir = bl_libs_dir.as_posix()
    usd_dir = repo_dir / "USD"

    if clean:
        rm_dir(usd_dir / "build")

    cur_dir = os.getcwd()
    os.chdir(str(usd_dir))

    try:
        check_call('git', 'apply', '--whitespace=nowarn', str(repo_dir / "usd.diff"))

        PYTHON_SHORT_VERSION_NO_DOTS = 310
        BOOST_VERSION_SHORT = 180
        BOOST_COMPILER_STRING = "-vc142"

        PYTHON_POSTFIX = "_d" if build_var == 'debug' else ""
        OPENEXR_VERSION_POSTFIX = "_d" if build_var == 'debug' else ""
        LIBEXT = ".lib" if OS == 'Windows' else ".a"
        LIBPREFIX = "" if OS == 'Windows' else "lib"
        SHAREDLIBEXT = ".lib" if OS == 'Windows' else ""
        PYTHON_EXTENSION = ".exe" if OS == 'Windows' else ""

        USD_CXX_FLAGS = "/DOIIO_STATIC_DEFINE /DOSL_STATIC_DEFINE"
        USD_PLATFORM_FLAGS = [f"-DCMAKE_CXX_FLAGS={USD_CXX_FLAGS}",
                              "-D_PXR_CXX_DEFINITIONS=/DBOOST_ALL_NO_LIB",
                              f"-DCMAKE_SHARED_LINKER_FLAGS_INIT=/LIBPATH:{bl_libs_dir}/tbb/lib",
                              "-DPython_FIND_REGISTRY=NEVER",
                              f"-DPYTHON_INCLUDE_DIRS={bl_libs_dir}/python/{PYTHON_SHORT_VERSION_NO_DOTS}/include",
                              f"-DPYTHON_LIBRARY={bl_libs_dir}/python/{PYTHON_SHORT_VERSION_NO_DOTS}/libs/python{PYTHON_SHORT_VERSION_NO_DOTS}{PYTHON_POSTFIX}{LIBEXT}"
        ]

        DEFAULT_BOOST_FLAGS = [
            f"-DBoost_COMPILER:STRING={BOOST_COMPILER_STRING}",
            "-DBoost_USE_MULTITHREADED=ON",
            "-DBoost_USE_STATIC_LIBS=OFF",
            "-DBoost_USE_STATIC_RUNTIME=OFF",
            f"-DBOOST_ROOT={bl_libs_dir}/boost",
            "-DBoost_NO_SYSTEM_PATHS=ON",
            "-DBoost_NO_BOOST_CMAKE=ON",
            f"-DBoost_ADDITIONAL_VERSIONS={BOOST_VERSION_SHORT}",
            f"-DBOOST_LIBRARYDIR={bl_libs_dir}/boost/lib/",
            "-DBoost_USE_DEBUG_PYTHON=On"
        ]

        USD_EXTRA_ARGS = [*DEFAULT_BOOST_FLAGS,
                          *USD_PLATFORM_FLAGS,
                          f"-DOPENSUBDIV_ROOT_DIR={bl_libs_dir}/opensubdiv",
                          f"-DOpenImageIO_ROOT={bl_libs_dir}/openimageio",
                          f"-DOPENEXR_LIBRARIES={bl_libs_dir}/imath/lib/{LIBPREFIX}Imath{OPENEXR_VERSION_POSTFIX}{SHAREDLIBEXT}",
                          f"-DOPENEXR_INCLUDE_DIR={bl_libs_dir}/imath/include",
                          f"-DImath_DIR={bl_libs_dir}/imath",
                          f"-DOPENVDB_LOCATION={bl_libs_dir}/openvdb",
                          "-DPXR_ENABLE_PYTHON_SUPPORT=ON",
                          "-DPXR_USE_PYTHON_3=ON",
                          "-DPXR_BUILD_IMAGING=ON",
                          "-DPXR_BUILD_TESTS=OFF",
                          "-DPXR_BUILD_EXAMPLES=OFF",
                          "-DPXR_BUILD_TUTORIALS=OFF",
                          "-DPXR_BUILD_USDVIEW=OFF",
                          "-DPXR_ENABLE_HDF5_SUPPORT=OFF",
                          "-DPXR_ENABLE_MATERIALX_SUPPORT=ON",
                          "-DPXR_ENABLE_OPENVDB_SUPPORT=ON",
                          f"-DPYTHON_EXECUTABLE={sys.executable}",
                          "-DPXR_BUILD_MONOLITHIC=ON",
                          # OSL is an optional dependency of the Imaging module. However, since that
                          # module was included for its support for converting primitive shapes (sphere,
                          # cube, etc.) to geometry, it's not necessary. Disabling it will make it
                          # simpler to build Blender; currently only Cycles uses OSL.
                          "-DPXR_ENABLE_OSL_SUPPORT=OFF",
                          # Enable OpenGL for Hydra support. Note that this indirectly also adds an X11
                          # dependency on Linux. This would be good to eliminate for headless and Wayland
                          # only builds, however is not worse than what Blender already links to for
                          # official releases currently.
                          "-DPXR_ENABLE_GL_SUPPORT=ON",
                          # OIIO is used for loading image textures in Hydra Storm / Embree renderers.
                          "-DPXR_BUILD_OPENIMAGEIO_PLUGIN=ON",
                          # USD 22.03 does not support OCIO 2.x
                          # Tracking ticket https://github.com/PixarAnimationStudios/USD/issues/1386
                          "-DPXR_BUILD_OPENCOLORIO_PLUGIN=OFF",
                          "-DPXR_ENABLE_PTEX_SUPPORT=OFF",
                          "-DPXR_BUILD_USD_TOOLS=OFF",
                          "-DCMAKE_DEBUG_POSTFIX=_d",
                          "-DBUILD_SHARED_LIBS=ON",
                          f"-DTBB_INCLUDE_DIRS={bl_libs_dir}/tbb/include",
                          f"-DTBB_LIBRARIES={bl_libs_dir}/tbb/lib/{LIBPREFIX}tbb{SHAREDLIBEXT}",
                          f"-DTbb_TBB_LIBRARY={bl_libs_dir}/tbb/lib/{LIBPREFIX}tbb{SHAREDLIBEXT}",
                          f"-DTBB_tbb_LIBRARY_RELEASE={bl_libs_dir}/tbb/lib/{LIBPREFIX}tbb{SHAREDLIBEXT}",
                          # USD wants the tbb debug lib set even when you are doing a release build
                          # Otherwise it will error out during the cmake configure phase.
                          f"-DTBB_LIBRARIES_DEBUG={bl_libs_dir}/tbb/lib/{LIBPREFIX}tbb{SHAREDLIBEXT}",
                          f"-DBoost_INCLUDE_DIR={bl_libs_dir}/boost/include",
                          f"-DMaterialX_DIR={bin_dir}/USD/install/lib/cmake/MaterialX",
        ]


        try:
            _cmake(usd_dir, compiler, jobs, build_var, [
                *USD_EXTRA_ARGS,
                f'-DCMAKE_INSTALL_PREFIX={bin_dir / "USD/install"}',
            ])

        finally:
            print("Reverting USD repo")
            check_call('git', 'checkout', '--', '*')
            check_call('git', 'clean', '-f')

    finally:
        os.chdir(cur_dir)


def hdrpr(bl_libs_dir, bin_dir, compiler, jobs, clean, build_var):
    print_start("Building HdRPR")

    hdrpr_dir = repo_dir / "RadeonProRenderUSD"
    usd_dir = bin_dir / "USD/install"

    if clean:
        rm_dir(hdrpr_dir / "build")

    os.environ['PXR_PLUGINPATH_NAME'] = str(usd_dir / "lib/usd")

    PYTHON_SHORT_VERSION_NO_DOTS = 310
    BOOST_VERSION_SHORT = 180
    BOOST_COMPILER_STRING = "-vc142"

    PYTHON_POSTFIX = "_d" if build_var == 'debug' else ""
    OPENEXR_VERSION_POSTFIX = "_d" if build_var == 'debug' else ""
    LIBEXT = ".lib" if OS == 'Windows' else ".a"
    LIBPREFIX = "" if OS == 'Windows' else "lib"
    SHAREDLIBEXT = ".lib" if OS == 'Windows' else ""
    PYTHON_EXTENSION = ".exe" if OS == 'Windows' else ""

    path_str = ""
    for deps in ['imath/bin', 'openexr/bin', 'openvdb/bin', 'OpenImageIO/bin', 'tbb/bin', 'boost/lib', 'MaterialX/bin']:
        path_str += f"{bl_libs_dir / deps}" + os.pathsep

    path_str += f"{bin_dir / 'USD/install/lib'}" + os.pathsep
    os.environ['PATH'] = path_str + os.environ['PATH']

    cur_dir = os.getcwd()
    try:
        ch_dir(hdrpr_dir)
        check_call('git', 'apply', '--whitespace=nowarn', str(repo_dir / "hdRpr.diff"))

        DEFAULT_BOOST_FLAGS = [
            f"-DBoost_COMPILER:STRING={BOOST_COMPILER_STRING}",
            "-DBoost_USE_MULTITHREADED=ON",
            "-DBoost_USE_STATIC_LIBS=OFF",
            "-DBoost_USE_STATIC_RUNTIME=OFF",
            f"-DBOOST_ROOT={bl_libs_dir}/boost",
            "-DBoost_NO_SYSTEM_PATHS=ON",
            "-DBoost_NO_BOOST_CMAKE=ON",
            f"-DBoost_ADDITIONAL_VERSIONS={BOOST_VERSION_SHORT}",
            f"-DBOOST_LIBRARYDIR={bl_libs_dir}/boost/lib/",
            "-DBoost_USE_DEBUG_PYTHON=On"
        ]

        _cmake(hdrpr_dir, compiler, jobs, build_var, [
            *DEFAULT_BOOST_FLAGS,
            f'-Dpxr_DIR={usd_dir}',
            f'-DCMAKE_INSTALL_PREFIX={bin_dir}/USD/install',
            '-DRPR_BUILD_AS_HOUDINI_PLUGIN=FALSE',
            f'-DPYTHON_EXECUTABLE={sys.executable}',
            f"-DIMATH_INCLUDE_DIR={bl_libs_dir}/imath/include/imath",
            f"-DOPENEXR_INCLUDE_DIR={bl_libs_dir}/openexr/include/OpenEXR",
            f"-DBoost_INCLUDE_DIR={bl_libs_dir}/boost/include",
            f"-DImath_DIR={bl_libs_dir}/imath",
            '-DPXR_BUILD_MONOLITHIC=ON',
            f'-DUSD_LIBRARY_DIR={usd_dir}/lib',
            f'-DUSD_MONOLITHIC_LIBRARY={usd_dir / "lib" / ("usd_ms_d.lib" if build_var == "debug" else "usd_ms.lib")}',
            f"-DTBB_LIBRARY={bl_libs_dir}/tbb/lib/{LIBPREFIX}tbb{SHAREDLIBEXT}",
            f"-DTBB_INCLUDE_DIR={bl_libs_dir}/tbb/include",
        ])

    finally:
        check_call('git', 'checkout', '--', '*')
        ch_dir(cur_dir)


def zip_addon(bin_dir):
    print_start("Creating zip Addon")

    # region internal functions

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

        # copy hipbin folder
        hipbin_dir = hydrarpr_repo_dir / 'deps/RPR/hipbin'
        for f in hipbin_dir.glob("**/*"):
            if f.name in ('.git', '.gitattributes'):
                continue

            yield f, f'libs/plugin/usd/rprUsd/resources/ns_kernels/{f.name}'

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

        # copy python rpr
        pyrpr_dir = bin_dir / 'USD/install/lib/python/rpr'
        (pyrpr_dir / "RprUsd/__init__.py").write_text("")
        for f in (pyrpr_dir / "__init__.py", pyrpr_dir / "RprUsd/__init__.py"):
            yield f, Path("libs") / f.relative_to(pyrpr_dir.parent.parent)

    def get_version():
        # getting buid version
        build_ver = subprocess.getoutput("git rev-parse --short HEAD")

        # # getting plugin version
        # text = (repo_dir / "src/hdusd/__init__.py").read_text()
        # m = re.search(r'"version": \((\d+), (\d+), (\d+)\)', text)
        # plugin_ver = m.group(1), m.group(2), m.group(3)
        #
        # return (*plugin_ver, build_ver)

        return build_ver

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

    # endregion

    repo_dir = Path(__file__).parent
    install_dir = repo_dir / "install"
    ver = get_version()
    name = f"hydrarpr-{ver}-{OS.lower()}.zip"

    if install_dir.is_dir():
        for file in os.listdir(install_dir):
            if file == name:
                os.remove(install_dir / file)
                break
    else:
        install_dir.mkdir()

    zip_addon = create_zip_addon(install_dir, bin_dir, name, ver)
    print(f"Addon was compressed to: {zip_addon}")


def main():
    ap = argparse.ArgumentParser()

    # Add the arguments to the parser
    ap.add_argument("-all", required=False, action="store_true",
                    help="Build all")
    ap.add_argument("-materialx", required=False, action="store_true",
                    help="Build MaterialX")
    ap.add_argument("-usd", required=False, action="store_true",
                    help="Build USD")
    ap.add_argument("-hdrpr", required=False, action="store_true",
                    help="Build HdRPR")
    ap.add_argument("-bl-libs-dir", required=False, type=str, default="",
                    help="Path to root of Blender libs directory"),
    ap.add_argument("-bin-dir", required=False, type=str, default="",
                    help="Path to binary directory")
    ap.add_argument("-addon", required=False, action="store_true",
                    help="Create zip addon")
    ap.add_argument("-G", required=False, type=str,
                    help="Compiler for HdRPR and MaterialX in cmake. "
                         'For example: -G "Visual Studio 16 2019"',
                    default="Visual Studio 16 2019" if OS == 'Windows' else "")
    ap.add_argument("-j", required=False, type=int, default=0,
                    help="Number of jobs run in parallel")
    ap.add_argument("-build-var", required=False, type=str, default="release",
                    choices=('release', 'relwithdebuginfo'),  # TODO: add 'debug' build variant
                    help="Build variant for USD, HdRPR and dependencies. (default: release)")
    ap.add_argument("-clean", required=False, action="store_true",
                    help="Clean build dirs before start USD or HdRPR build")

    args = ap.parse_args()

    bl_libs_dir = Path(args.bl_libs_dir).absolute().resolve()

    bin_dir = Path(args.bin_dir).resolve() if args.bin_dir else (repo_dir / "bin")
    bin_dir = bin_dir.absolute()
    bin_dir.mkdir(parents=True, exist_ok=True)

    if args.all or args.materialx:
        materialx(bin_dir, args.G, args.j, args.clean, args.build_var)

    if args.all or args.usd:
        usd(bl_libs_dir, bin_dir, args.G, args.j, args.clean, args.build_var)

    if args.all or args.hdrpr:
        hdrpr(bl_libs_dir, bin_dir, args.G, args.j, args.clean, args.build_var)

    if args.all or args.addon:
        zip_addon(bin_dir)

    print_start("Finished")


if __name__ == "__main__":
    main()
