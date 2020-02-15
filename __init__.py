import os
import sys
import matplotlib as mpl

currentPath = os.path.dirname( __file__ )
sys.path.append(os.path.abspath(currentPath))

# Setting backend
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'F:\Program Files\QGIS 3.10\apps\Qt5\plugins'
os.environ['PATH'] += r';F:\Program Files\QGIS 3.10\apps\qgis\bin;~qgis directory\apps\Qt5\bin'
mpl.use('Qt5Agg')


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FractureAnalysis2D class from file FractureAnalysis2D.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fracture_analysis_2d import FractureAnalysis2D
    return FractureAnalysis2D(iface)
