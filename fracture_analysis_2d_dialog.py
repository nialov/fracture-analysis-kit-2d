import os

from qgis.PyQt import QtWidgets
from qgis.PyQt import uic

# from .fracture_analysis_2d import load_FORM_CLASS

# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
# FORM_CLASS, _ = uic.loadUiType(os.path.join(
#     os.path.dirname(__file__), 'fracture_analysis_2d_dialog_base.ui'))

def get_FractureAnalysis2DDialog():
    FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'fracture_analysis_2d_dialog_base.ui'))

    class FractureAnalysis2DDialog(QtWidgets.QDialog, FORM_CLASS):
        def __init__(self, parent=None):
            """Constructor."""
            super(FractureAnalysis2DDialog, self).__init__(parent)
            # Set up the user interface from Designer through FORM_CLASS.
            # After self.setupUi() you can access any designer object by doing
            # self.<objectname>, and you can use autoconnect slots - see
            # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
            # #widgets-and-dialogs-with-auto-connect
            self.setupUi(self)
    return FractureAnalysis2DDialog()

