import os
import sys
from pathlib import Path
from qgis.PyQt.QtWidgets import QMessageBox


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FractureAnalysis2D class from file FractureAnalysis2D.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    currentPath = os.path.dirname(__file__)
    install_dir = str((Path(__file__) / Path("install_dir")).resolve())
    sys.path.append(os.path.abspath(currentPath))

    # Setup Pythonpath for when user has no administrator access and installed modules are in user Python folder.
    roaming_folder = os.environ['APPDATA']

    # Add custom pyproj proj.db installation to PROJ_LIB to avoid conflicts and issues with not found proj.db.
    # TODO: Implement better PROJ_LIB if needed?...............

    try:
        os.environ['PYTHONPATH'] += rf';{roaming_folder}\Python\Python37\site-packages;{install_dir}'
    except KeyError:
        os.environ['PYTHONPATH'] = rf'{roaming_folder}\Python\Python37\site-packages;{install_dir}'

    # Checks if external Python modules are installed and functional.
    from install_script import check_installations
    try:
        check_installations()
    except ModuleNotFoundError as e:
        QMessageBox.critical(None, "ModuleNotFoundError. One of more of the required Python modules are not found.\n"
                                   "Open OSGeo4WShell as administrator. Run:\npy3_env\n "
                                   "Then cd to this plugin's directory:\n"
                                   "cd 'input plugin directory' \n"
                                   "and then, run:\n"
                                   "python install_script.py\n"
                             , f'\n {e}')
        return



    from .fracture_analysis_2d import FractureAnalysis2D

    return FractureAnalysis2D(iface)



