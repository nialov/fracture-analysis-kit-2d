import os
import sys
import matplotlib as mpl

# Setup Path
currentPath = os.path.dirname( __file__ )
sys.path.append(os.path.abspath(currentPath))

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FractureAnalysis2D class from file FractureAnalysis2D.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fracture_analysis_2d import FractureAnalysis2D
    return FractureAnalysis2D(iface)
