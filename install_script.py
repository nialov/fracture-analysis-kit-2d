import subprocess
import sys
import os
import platform
from pathlib import Path

gdal_64 = r"GDAL-3.0.4-cp37-cp37m-win_amd64.whl"
gdal_32 = r"GDAL-3.0.4-cp37-cp37m-win32.whl"
fiona_64 = r"Fiona-1.8.13-cp37-cp37m-win_amd64.whl"
fiona_32 = r"Fiona-1.8.13-cp37-cp37m-win32.whl"
install_dir = "install_dir"


# def download_external(is_64):
#     dl_dir = "py_downloads"
#     if Path(dl_dir).exists():
#         pass
#     else:
#         os.mkdir(dl_dir)


def pip_install_all(is_64, gdal_needed):
    """
    Installs all requirements using pip.

    :param is_64: Is platform 64 bit
    :type is_64: bool
    :param gdal_needed: Is gdal needed for install
    :type gdal_needed: bool
    """
    os.chdir(Path(install_dir))
    base_install_these = ["geopandas", "python-ternary", "sklearn", "seaborn", "powerlaw"]
    if is_64 and gdal_needed:
        install_these = [gdal_64, fiona_64] + base_install_these
    elif is_64:
        install_these = [fiona_64] + base_install_these
    elif gdal_needed:
        install_these = [gdal_32, fiona_32] + base_install_these
    else:
        install_these = [fiona_32] + base_install_these

    for inst in install_these:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', inst, "--user"])

def is_installation_needed():
    try:
        import gdal
        import fiona
        import geopandas
        try:
            import ternary
        except ModuleNotFoundError as e:
            if "_tkinter" in str(e):
                pass
            else:
                raise
        import sklearn
        try:
            import seaborn
        except ModuleNotFoundError as e:
            if "_tkinter" in str(e):
                pass
            else:
                raise
    except:
        return True
    return False

def check_installations():
    import gdal
    import fiona
    import geopandas
    try:
        import ternary
    except ModuleNotFoundError as e:
        if "_tkinter" in str(e):
            pass
        else:
            raise
    import sklearn
    try:
        import seaborn
    except ModuleNotFoundError as e:
        if "_tkinter" in str(e):
            pass
        else:
            raise

def is_gdal_needed():
    """
    Checks if gdal is installed and functional for external Python plugins.

    TODO: Check except clause.

    :return: True or False
    :rtype: bool
    """
    try:
        import gdal
    except:
        return True
    return False


def verify_external_downloads(is_64, gdal_needed):
    """
    Verify if user has downloaded required unofficial Windows binaries from:
    https://www.lfd.uci.edu/~gohlke/pythonlibs/

    :param is_64: Is platform 64 or 32 bit
    :type is_64: bool
    :param gdal_needed: Is gdal up and running already.
    :type gdal_needed: bool
    :return: True if binaries are found.
    :rtype: bool
    :raise FileNotFoundError: If binaries or install directory are not found relative to the script.
    """
    if Path(install_dir).exists():
        pass
    else:
        raise FileNotFoundError(f"Install directory not found: \n"
                                f"{install_dir}")
    if is_64:
        if gdal_needed:
            if (Path(install_dir) / Path(gdal_64)).exists():
                pass
            else:
                raise FileNotFoundError(f"Fiona 64bit .whl not found.\n"
                                        f"In: {Path(install_dir) / Path(fiona_64)}\n"
                                        f"Download from: \n"
                                        f"https://www.lfd.uci.edu/~gohlke/pythonlibs/")

        if (Path(install_dir) / Path(fiona_64)).exists():
            pass
        else:
            raise FileNotFoundError(f"Fiona 64bit .whl not found.\n"
                                    f"In: {Path(install_dir) / Path(fiona_64)}\n"
                                    f"Download from: \n"
                                    f"https://www.lfd.uci.edu/~gohlke/pythonlibs/")
    else:
        if gdal_needed:
            if (Path(install_dir) / Path(gdal_32)).exists():
                pass
            else:
                raise FileNotFoundError(f"Fiona 32bit .whl not found.\n"
                                        f"In: {Path(install_dir) / Path(fiona_32)}\n"
                                        f"Download from: \n"
                                        f"https://www.lfd.uci.edu/~gohlke/pythonlibs/")

        if (Path(install_dir) / Path(fiona_32)).exists():
            pass
        else:
            raise FileNotFoundError(f"Fiona 32bit .whl not found.\n"
                                    f"In: {Path(install_dir) / Path(fiona_32)}\n"
                                    f"Download from: \n"
                                    f"https://www.lfd.uci.edu/~gohlke/pythonlibs/")


def install():
    """
    Main installation method. Prints messages to stdout.
    """
    print("Installation setup beginning.")
    needed = is_installation_needed()
    if needed:
        # Makes sure path is setup.
        os.chdir(Path(__file__).parent)
        # Does gdal need external installation
        gdal_needed = is_gdal_needed()
        # Is the platform 64 or 32 bit
        is_64 = True if platform.architecture()[0] == "64bit" else False
        # User must download manually files from https://www.lfd.uci.edu/~gohlke/pythonlibs/
        # Will throw FileNotFoundErrors for all not found files.
        print("Verifying if external downloads are found.")
        verify_external_downloads(is_64, gdal_needed)
        print("Starting installation of modules. Will take some time (minute[s]) "
              "depending on computer and internet connection.")
        pip_install_all(is_64, gdal_needed)
        print("Installation done.")
        print("Testing installations.")
        check_installations()
        print("Installation Successful!")
    else:
        print("All needed modules seem functional. No installation required.")


if __name__ == '__main__':
    install()
