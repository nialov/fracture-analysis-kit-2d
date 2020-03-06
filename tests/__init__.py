"""Tests for kit modules"""
import os, sys
sys.path.insert(0, os.path.abspath('.'))
print(os.path.abspath('.'))

import matplotlib
# IMPORTANT! Change this to your own path if testing or remaking docs is required.
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'F:\Program Files\QGIS 3.10\apps\Qt5\plugins'
matplotlib.use('Qt5Agg')

sys.path.insert(0, r'F:\Program Files\QGIS 3.10\apps\Qt5')
sys.path.insert(0, r'F:\Program Files\QGIS 3.10\apps')