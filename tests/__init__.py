"""Tests for kit modules"""
import os, sys
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
print(os.path.abspath('.'))

import matplotlib

# IMPORTANT! Change these to your own paths if testing or remaking docs is required.
# TODO: OSGEO4W_ROOT env variable exists but is difficult to implement due to windows path management errors.
qt5_plugins = Path(r'F:\OSGeo4W64\apps\Qt5\plugins')
qt5_path = Path(r'F:\OSGeo4W64\apps\Qt5')
qgis_apps_path = Path(r'F:\OSGeo4W64\apps')
os.environ["PROJ_LIB"] += r";F:\OSGeo4W64\apps\Python37\lib\site-packages\pyproj\proj_dir\share\proj"

# qt5_plugins = Path(os.environ["OSGEO4W_ROOT"]) / Path(r'apps\Qt5\plugins')
# qt5_path = Path(os.environ["OSGEO4W_ROOT"]) / Path(r'apps\Qt5')
# qgis_apps_path = Path(os.environ["OSGEO4W_ROOT"]) / Path(r'apps')

if qt5_plugins.exists() and qt5_path.exists() and qgis_apps_path.exists():
    pass
else:
    raise NotADirectoryError(f"User defined path variables: {qt5_plugins}\n{qt5_path}\n{qgis_apps_path}\n"
                             f"Directory or directories do not exist."
                             rf"Setup the variables to the correct folders.")

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(qt5_plugins)

matplotlib.use('Qt5Agg')

sys.path.insert(0, str(qt5_path))
sys.path.insert(0, str(qgis_apps_path))

