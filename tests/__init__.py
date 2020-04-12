"""Tests for kit modules"""
import os, sys
from pathlib import Path
sys.path.insert(0, os.path.abspath('.'))
print(os.path.abspath('.'))

import matplotlib

# IMPORTANT! Change these to your own paths if testing or remaking docs is required.
own_path = Path(r'F:\OSGeo4W64\apps\Qt5\plugins')
qt5_path = Path(r'F:\OSGeo4W64\apps\Qt5')
qgis_apps_path = Path(r'F:\OSGeo4W64\apps')

if own_path.exists() and qt5_path.exists() and qgis_apps_path.exists():
    pass
else:
    raise NotADirectoryError(f"User defined path variables: {own_path}\n{qt5_path}\n{qgis_apps_path}\n"
                             f"Directory or directories do not exist."
                             rf"Setup the variables to the correct folders.")

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = str(own_path)
matplotlib.use('Qt5Agg')

sys.path.insert(0, str(qt5_path))
sys.path.insert(0, str(qgis_apps_path))