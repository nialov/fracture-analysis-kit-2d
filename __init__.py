import os
import sys


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FractureAnalysis2D class from file FractureAnalysis2D.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    currentPath = os.path.dirname(__file__)
    sys.path.append(os.path.abspath(currentPath))

    # Setup Pythonpath for when user has no administrator access and modules are in user Python folder
    roaming_folder = os.environ['APPDATA']
    try:
        os.environ['PYTHONPATH'] += rf';{roaming_folder}\Python\Python37\site-packages'
    except KeyError:
        os.environ['PYTHONPATH'] = rf'{roaming_folder}\Python\Python37\site-packages'

    from .fracture_analysis_2d import FractureAnalysis2D

    return FractureAnalysis2D(iface)



