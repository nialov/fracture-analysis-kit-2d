"""
Main interface manipulator, handles all buttons and runs fracture_analysis_kit/main.py module
to start analysis and plotting.
"""


import os.path
import webbrowser

import pandas as pd
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction, QFileDialog, QTableWidgetItem, QMessageBox, QProgressBar, QProgressDialog
from qgis.core import QgsProject, Qgis, QgsVectorLayer, QgsMessageLog
from qgis.PyQt import uic

# Initialize Qt resources from file resources.py
from .resources import *

# Import the code for the dialog
from fracture_analysis_2d_dialog import get_FractureAnalysis2DDialog
from fracture_analysis_kit import main

# FORM_CLASS setup
# This loads your .ui file so that PyQt can populate your plugin with the elements from Qt Designer
def load_FORM_CLASS():
    FORM_CLASS, _ = uic.loadUiType(os.path.join(
        os.path.dirname(__file__), 'fracture_analysis_2d_dialog_base.ui'))
    return FORM_CLASS

class FractureAnalysis2D:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value("locale/userLocale")[0:2]
        locale_path = os.path.join(
            self.plugin_dir, "i18n", "FractureAnalysis2D_{}.qm".format(locale)
        )

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr("&2D Fracture Analysis Kit")

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        # Own variables for storing
        self.line_layers = None
        self.polygon_layers = None
        self.point_layers = None
        self.layer_table_df = pd.DataFrame(columns=['Trace', 'Branch', 'Node', 'Area', 'Name', 'Group'])
        self.group_names_cutoffs_df = pd.DataFrame(columns=['Group', 'CutOffTraces', 'CutOffBranches'])
        self.set_df = pd.DataFrame(columns=['Set', 'SetLimits'])


    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate("FractureAnalysis2D", message)

    def add_action(
            self,
            icon_path,
            text,
            callback,
            enabled_flag=True,
            add_to_menu=True,
            add_to_toolbar=True,
            status_tip=None,
            whats_this=None,
            parent=None,
    ):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToVectorMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """
        Create the menu entries and toolbar icons inside the QGIS GUI.

        """

        icon_path = ":/plugins/fracture_analysis_2d/icon.png"
        self.add_action(
            icon_path,
            text=self.tr(u"𝟮𝗗 𝗙𝗿𝗮𝗰𝘁𝘂𝗿𝗲 𝗔𝗻𝗮𝗹𝘆𝘀𝗶𝘀"),
            callback=self.run,
            parent=self.iface.mainWindow(),
        )

        # will be set False in run()
        self.first_start = True

    def unload(self):
        """
        Removes the plugin menu item and icon from QGIS GUI.
        """
        for action in self.actions:
            self.iface.removePluginVectorMenu(
                self.tr("&2D Fracture Analysis Kit"), action
            )
            self.iface.removeToolBarIcon(action)



    def select_output_folder(self, tab: int):
        """
        Used to select the output folder where a new folder for plots will be created.

        :param tab: Which tab in the interface.
        :type tab: int
        """
        outp = QFileDialog.getExistingDirectory(self.dlg, "Select output directory ")
        if type(outp) is (tuple or list):
            raise Exception("Multiple outputs from QFileDialog.getExistingDirectory")
        else:
            folder = outp
        if tab == 1:
            self.dlg.lineEdit_folder.setText(folder)
        elif tab == 2:
            self.dlg.lineEdit_tab2_folder.setText(folder)
        else:
            raise Exception('Invalid tab number given')

    def clear_group_name_cut_off_table(self):
        """
        Clear Group name and Cut Off table along with the complementary DataFrame.
        """
        for i in range(self.dlg.tableWidget_tab2_gnames.rowCount(), -1, -1):
            self.dlg.tableWidget_tab2_gnames.removeRow(i)
        self.dlg.tableWidget_tab2_gnames.clearContents()
        self.group_names_cutoffs_df = self.group_names_cutoffs_df.iloc[0:0]

    def populate_groups(self):
        """
        Populates group names to comboBox for target area layer grouping.
        """
        # Get group name list
        gname_list = self.group_names_cutoffs_df.Group.tolist()
        # Clear contents
        self.dlg.comboBox_tab2_gnames.clear()
        self.dlg.comboBox_tab2_gnames.addItems(gname_list)

    def add_row_layer(self):
        """
        Adds row to layer table and switches dummy layers to combo-boxes.
        """

        class DummyLayer(object):
            """
            Dummy layer for combo-box.
            """
            is_dummy = True

            def __init__(self):
                pass

            def name(self):
                return "---"

        # Additions
        name = self.dlg.lineEdit_tab2_tan.text()
        trace_layer = self.line_layers[self.dlg.comboBox_trace.currentIndex()]
        branch_layer = self.line_layers[self.dlg.comboBox_branch.currentIndex()]
        node_layer = self.point_layers[self.dlg.comboBox_node.currentIndex()]
        area_layer = self.polygon_layers[self.dlg.comboBox_area.currentIndex()]
        target_area_group = self.dlg.comboBox_tab2_gnames.currentText()
        # Substitute for blank names
        if name == "":
            name = trace_layer.name()
        # Verify inputs.

        for layer in [trace_layer, branch_layer, node_layer, area_layer]:
            if not isinstance(layer, QgsVectorLayer):
                QMessageBox.critical(None, "Error"
                                     , f'Dummy (= "---"-layer) or Non-vector layer chosen for addition\
                                      \nDo not choose {layer.name()} layer')
                return
        if len(target_area_group) == 0:
            QMessageBox.critical(None, "Error"
                                 , f'No Group chosen')
            return
        if name in self.layer_table_df.Name.tolist():
            QMessageBox.critical(None, "Error"
                                 , f'Given Target Area Name ({name}) is already in the layer table.'
                                   f'Duplicate names are not allowed.')
            return
        if name in self.group_names_cutoffs_df.Group.tolist():
            QMessageBox.critical(None, "Error"
                                 , f'Given Target Area Name ({name}) is already in the group names table.'
                                   f'Duplicate names are not allowed between target areas and groups.')
            return
        # Current row count
        curr_row = self.dlg.tableWidget_tab2.rowCount()
        # Add new row
        self.dlg.tableWidget_tab2.insertRow(curr_row)
        # Add data to table
        self.dlg.tableWidget_tab2.setItem(curr_row, 4, QTableWidgetItem(name))
        self.dlg.tableWidget_tab2.setItem(curr_row, 0, QTableWidgetItem(trace_layer.name()))
        self.dlg.tableWidget_tab2.setItem(curr_row, 1, QTableWidgetItem(branch_layer.name()))
        self.dlg.tableWidget_tab2.setItem(curr_row, 2, QTableWidgetItem(node_layer.name()))
        self.dlg.tableWidget_tab2.setItem(curr_row, 3, QTableWidgetItem(area_layer.name()))
        self.dlg.tableWidget_tab2.setItem(curr_row, 5, QTableWidgetItem(target_area_group))
        self.layer_table_df = self.layer_table_df.append(
            {'Trace': trace_layer, 'Branch': branch_layer, 'Node': node_layer
                , 'Area': area_layer, 'Name': name, 'Group': target_area_group}
            , ignore_index=True)
        # Switch list item with a dummy
        self.line_layers[self.dlg.comboBox_trace.currentIndex()] = DummyLayer()
        self.line_layers[self.dlg.comboBox_branch.currentIndex()] = DummyLayer()
        self.point_layers[self.dlg.comboBox_node.currentIndex()] = DummyLayer()
        self.polygon_layers[self.dlg.comboBox_area.currentIndex()] = DummyLayer()
        self.update_layers_tab2()

    def clear_layer_table(self):
        """
        Clears layer table and restores all layers to choices.
        """
        for i in range(self.dlg.tableWidget_tab2.rowCount(), -1, -1):
            self.dlg.tableWidget_tab2.removeRow(i)
        self.dlg.tableWidget_tab2.clearContents()

        self.layer_table_df = self.layer_table_df.iloc[0:0]
        self.fetch_correct_vector_layers()
        self.update_layers_tab2()

    def update_layers_tab2(self):
        """
        Updates layers to combo-boxes for tab2.
        """
        # Clear the contents of the comboBox from previous runs tab 2
        self.dlg.comboBox_trace.clear()
        self.dlg.comboBox_branch.clear()
        self.dlg.comboBox_node.clear()
        self.dlg.comboBox_area.clear()
        # Populate the comboBox with names of all the updated layers tab 2
        self.dlg.comboBox_trace.addItems([layer.name() for layer in self.line_layers])
        self.dlg.comboBox_branch.addItems([layer.name() for layer in self.line_layers])
        self.dlg.comboBox_node.addItems([layer.name() for layer in self.point_layers])
        self.dlg.comboBox_area.addItems([layer.name() for layer in self.polygon_layers])

    # def update_layers_tab1(self):
    #     """
    #     Updates layers to combo-boxes for tab1.
    #     """
    #     # Clear the contents of the comboBox from previous runs tab 2
    #     self.dlg.comboBox_trace.clear()
    #     self.dlg.comboBox_branch.clear()
    #     self.dlg.comboBox_node.clear()
    #     self.dlg.comboBox_area.clear()
    #     # Populate the comboBox with names of all the updated layers tab 2
    #     self.dlg.comboBox_trace.addItems([layer.name() for layer in self.line_layers])
    #     self.dlg.comboBox_branch.addItems([layer.name() for layer in self.line_layers])
    #     self.dlg.comboBox_node.addItems([layer.name() for layer in self.point_layers])
    #     self.dlg.comboBox_area.addItems([layer.name() for layer in self.polygon_layers])

    def add_row_group_name_cutoff(self):
        """
        Adds row to Group name Cut Off table with given inputs.
        """
        group_name = self.dlg.lineEdit_gname.text()
        cut_off_traces = self.dlg.lineEdit_tab2_cutoff_traces.text()
        cut_off_branches = self.dlg.lineEdit_tab2_cutoff_branches.text()
        # Validate inputs
        try:
            cut_off_traces_float = float(cut_off_traces)
        except ValueError:
            QMessageBox.critical(None, "Error"
                                 , f'Invalid trace Cut-off given: {cut_off_traces}\n'
                                   f'Give as meters  (e.g. 1.5)')
            return
        try:
            cut_off_branches_float = float(cut_off_branches)
        except ValueError:
            QMessageBox.critical(None, "Error"
                                 , f'Invalid branch Cut-off given: {cut_off_branches}\n'
                                   f'Give as meters  (e.g. 0.5)')
            return
        if len(group_name) == 0:
            QMessageBox.critical(None, "Error"
                                 , f'No Group name given')
            return
        if cut_off_traces == '':
            QMessageBox.critical(None, "Error"
                                 , f'No trace Cut-off value given')
            return
        if cut_off_branches == '':
            QMessageBox.critical(None, "Error"
                                 , f'No branch Cut-off value given')
            return
        if 0 > cut_off_traces_float:
            QMessageBox.critical(None, "Error"
                                 , f'Negative trace Cut-off value given: {cut_off_traces_float}\n'
                                   f'Give as meters (e.g. 0.95)')
            return
        if 0 > cut_off_branches_float:
            QMessageBox.critical(None, "Error"
                                 , f'Negative branch Cut-off value given: {cut_off_branches_float}\n'
                                   f'Give as meters (e.g. 0.95)')
            return
        if group_name in self.group_names_cutoffs_df.Group.tolist():
            QMessageBox.critical(None, "Error"
                                 , f'Given Group Name ({group_name}) is already in the group names table.'
                                   f'Duplicate names are not allowed.')
            return
        if group_name in self.layer_table_df.Name.tolist():
            QMessageBox.critical(None, "Error"
                                 , f'Given Group Name ({group_name}) is already in the layer table.'
                                   f'Duplicate names for target areas and groups are not allowed.')
            return
        # Current row count
        curr_row = self.dlg.tableWidget_tab2_gnames.rowCount()
        # Add new row
        self.dlg.tableWidget_tab2_gnames.insertRow(curr_row)
        # Add data
        self.dlg.tableWidget_tab2_gnames.setItem(curr_row, 0, QTableWidgetItem(group_name))
        self.dlg.tableWidget_tab2_gnames.setItem(curr_row, 1, QTableWidgetItem(cut_off_traces))
        self.dlg.tableWidget_tab2_gnames.setItem(curr_row, 2, QTableWidgetItem(cut_off_branches))
        # Append to DataFrame as float
        self.group_names_cutoffs_df = self.group_names_cutoffs_df.append({'Group': group_name
                                                                             , 'CutOffTraces': cut_off_traces_float
                                                                             , 'CutOffBranches': cut_off_branches_float}
                                                                         , ignore_index=True)
        # Populate names to target area group button
        self.populate_groups()
        # Clear name and cut_off text boxes
        self.dlg.lineEdit_gname.clear()
        self.dlg.lineEdit_tab2_cutoff_traces.clear()
        self.dlg.lineEdit_tab2_cutoff_branches.clear()

    def add_row_set(self):
        """
        Adds row to set table with given inputs.
        """
        set_start = self.dlg.lineEdit_tab2_set_start.text()
        set_end = self.dlg.lineEdit_tab2_set_end.text()
        # Verify addition
        try:
            set_start_float = float(set_start)
            set_end_float = float(set_end)
        except ValueError:
            QMessageBox.critical(None, "Error"
                                 , f'Invalid input: "{set_start, set_end}". Could not convert to float.\n'
                                   f'Give inputs as numerical values with dot as the decimal-separator.')
            return
        if (set_start == '') or (set_end == ''):
            QMessageBox.critical(None, "Error"
                                 , f'Input both set values.')
            return
        if (not 180 >= set_start_float >= 0) or (not 180 >= set_end_float >= 0):
            QMessageBox.critical(None, "Error"
                                 , f'Invalid set range given (Input must be degrees between 0 and 180)')
            return
        # Set name and limits
        set_name = str(self.set_df.shape[0] + 1)
        set_limits = f'[{set_start}, {set_end}]'
        # Current row count
        curr_row = self.dlg.tableWidget_tab2_sets.rowCount()
        # Add new row
        self.dlg.tableWidget_tab2_sets.insertRow(curr_row)
        # Add data
        self.dlg.tableWidget_tab2_sets.setItem(curr_row, 0, QTableWidgetItem(set_name))
        self.dlg.tableWidget_tab2_sets.setItem(curr_row, 1, QTableWidgetItem(set_limits))
        # Append to DataFrame as floats
        self.set_df = self.set_df.append({'Set': set_name, 'SetLimits': (set_start_float, set_end_float)},
                                         ignore_index=True)
        # Clear name and limits text boxes
        self.dlg.lineEdit_tab2_set_start.clear()
        self.dlg.lineEdit_tab2_set_end.clear()
        self.dlg.lineEdit_tab2_set_start.setText('125')
        self.dlg.lineEdit_tab2_set_end.setText('170')

    def clear_set_table(self):
        """
        Clears set table.
        """
        self.dlg.tableWidget_tab2_sets.clearContents()
        self.set_df = self.set_df.iloc[0:0]

    def fetch_correct_vector_layers(self):
        """
        Fetches current layers and checks which ones are suitable for which comboBox selection.
        E.g. Only VectorLayers are suitable, no raster layers in any comboBox selection and only VectorLayers
        with LineStrings or MultiLineStrings are suitable for traces and branches.
        """
        # Fetch the currently loaded layers
        layers = QgsProject.instance().mapLayers().values()

        # Filter to only vector layers UNUSED
        vector_layers = []
        # Filter to polyline, point and polygon layers
        line_layers, point_layers, polygon_layers = [], [], []
        for layer in layers:
            # layer.type() returns an integer to point to the layer type in older QGIS versions.
            # This must be taken into account.
            # 0 == VectorLayer
            if "VectorLayer" in str(layer.type()) or "0" == str(layer.type()):
                vector_layers.append(layer)
                layer_features_iter = layer.getFeatures()
                # Find feature type by checking the geometry of the first item in the geometry column of the layer
                for feature in layer_features_iter:
                    if 'String' in str(feature.geometry()):
                        line_layers.append(layer)
                        break
                    elif 'PointZ' in str(feature.geometry()):
                        point_layers.append(layer)
                        break
                    elif 'Polygon' in str(feature.geometry()):
                        polygon_layers.append(layer)
                        break
        # Save as class attributes
        self.line_layers, self.point_layers, self.polygon_layers, = line_layers, point_layers, polygon_layers

    # def create_progress_dialog(self):
    #     dialog = QProgressDialog()
    #     dialog.setWindowTitle("Analysis Progress")
    #     dialog.setLabelText("Note: Only a rough indicator")
    #     bar = QProgressBar(dialog)
    #     bar.setTextVisible(True)
    #     bar.setValue(0)
    #     dialog.setBar(bar)
    #     dialog.setMinimumWidth(300)
    #     dialog.show()
    #     return dialog, bar

    def open_help_doc(self):
        """
        Opens help documentation when ? is clicked.
        """
        current_dir = os.path.dirname(__file__)
        webbrowser.open(url=fr'{current_dir}\docs\index.html', new=2)

    def run(self):
        """
        Run method that performs the dialog event loop.
        """

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False
            self.dlg = get_FractureAnalysis2DDialog()
            # self.dlg = FractureAnalysis2DDialog()
            # self.dlg.pushButton.clicked.connect(lambda: self.select_output_folder(1))
            '''-------------Multi Target Area----------------'''
            # Select output folder for Multi Target Area
            self.dlg.pushButton_tab2_folder.clicked.connect(lambda: self.select_output_folder(2))
            # Clear group name table from prev runs
            self.dlg.tableWidget_tab2_gnames.clearContents()
            # Clear group name list
            self.dlg.pushButton_gname_clear.clicked.connect(self.clear_group_name_cut_off_table)
            # Add row to table for layers and info
            self.dlg.pushButton_tab2_add_row_layers.clicked.connect(self.add_row_layer)
            # Clear table
            self.dlg.pushButton_tab2_table_clear.clicked.connect(self.clear_layer_table)
            # Run multi-target analysis
            self.dlg.pushButton_tab2_run.clicked.connect(self.run_multi_target_analysis)
            # Add row to table for group names and cut offs
            self.dlg.pushButton_gname_add.clicked.connect(self.add_row_group_name_cutoff)
            # Add azimuth set
            self.dlg.pushButton_tab2_set_add.clicked.connect(self.add_row_set)
            # Clear set table
            self.dlg.pushButton_tab2_set_clear.clicked.connect(self.clear_set_table)
            # Open Help Documentation
            self.dlg.pushButton_help.clicked.connect(self.open_help_doc)


            QgsMessageLog.logMessage(message="Plugin initialized.", tag=f'{__name__}', level=Qgis.Info)

        self.fetch_correct_vector_layers()
        self.update_layers_tab2()
        # self.update_layers_tab1()

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # TODO: Reimplement single target area using df functionality?
            QMessageBox.critical(None, "Error"
                                 , f'Single Target Area Analysis Not Implemented')
            return
            # # Do something useful here - delete the line containing pass and
            # # substitute with your code.
            # results_folder = self.dlg.lineEdit_folder.text()
            # name = self.dlg.lineEdit_name.text()

            # trace_layer = self.line_layers[self.dlg.comboBox_trace.currentIndex()]
            # branch_layer = self.line_layers[self.dlg.comboBox_branch.currentIndex()]
            # node_layer = self.point_layers[self.dlg.comboBox_node.currentIndex()]
            # area_layer = self.polygon_layers[self.dlg.comboBox_area.currentIndex()]
            #
            # # Start analysis
            #
            # _ = main_target_analysis.main_single_target_area(
            #     results_folder, name, trace_layer, branch_layer, node_layer, area_layer, self.debug_logger)
            #
            # # self.debug_logger.write_to_log_time('layer_table_df:' + str(self.layer_table_df))
            #
            # # Push finish message
            # self.iface.messageBar().pushMessage(
            #     "Success",
            #     f"Plots were of {name} made into {results_folder}",
            #     level=Qgis.Success,
            #     duration=10,
            # )

    def run_multi_target_analysis(self):
        """
        Starts analysis and doesn't stop until plots have been all saved to folder.
        Will push a finish message when done.
        """

        # Log start
        QgsMessageLog.logMessage(message="Multi Target Analysis started.", tag=f'{__name__}', level=Qgis.Info)
        # Output folder
        results_folder = self.dlg.lineEdit_tab2_folder.text()
        # Analysis name
        analysis_name = self.dlg.lineEdit_tab2_analysis_name.text()
        # Validate inputs
        if len(results_folder) == 0 or len(analysis_name) == 0:
            QMessageBox.critical(None, "Error"
                                 , f'Empty results folder or analysis name inputs: {results_folder, analysis_name}\n'
                                   f'Try again with fixed inputs.')
            return
        if len(self.layer_table_df) == 0:
            QMessageBox.critical(None, "Error"
                                 , f'Empty trace, branch and area layer table.')
            return
        if len(self.group_names_cutoffs_df) == 0:
            QMessageBox.critical(None, "Error"
                                 , f'Empty Group name and Cut-off table.')
            return
        if len(self.set_df) == 0:
            qb = QMessageBox
            reply = qb.question(None, 'Alert!', 'No set ranges given. Continue with default sets?', qb.No, qb.Yes)
            if reply == qb.No:
                return
            elif reply == qb.Yes:
                # Default set ranges
                self.set_df = self.set_df.append({'Set': str(1), 'SetLimits': (45, 90)},
                                                 ignore_index=True)
                self.set_df = self.set_df.append({'Set': str(2), 'SetLimits': (125, 170)},
                                                 ignore_index=True)
                self.set_df = self.set_df.append({'Set': str(3), 'SetLimits': (171, 15)},
                                                 ignore_index=True)
            else:
                return

        # Invalidate inputs when there are groups without any target areas.
        if len(set(self.group_names_cutoffs_df.Group) & set(self.layer_table_df.Group)) \
                != len(set(self.group_names_cutoffs_df.Group)):
            QMessageBox.critical(None, "Error"
                                 , f'Group names without target areas are not allowed.')
            return

        # Run analysis
        main.main_multi_target_area(self.layer_table_df, results_folder, analysis_name,
                                    self.group_names_cutoffs_df,
                                    self.set_df)
        # TODO: Implement tasks (traces and branches)?
        # Run as task
        # main_target_analysis.task_main_multi_target_area(self.layer_table_df, results_folder, analysis_name,
        #                                             self.group_names_cutoffs_df,
        #                                             self.set_df, self.debug_logger)

        # Push finish message
        QMessageBox.information(None, "Success!"
                                , f'Plots of {analysis_name} were made into {results_folder}.')
        # self.iface.messageBar().pushMessage(
        #     "Success",
        #     f"Plots were of {analysis_name} made into {results_folder}",
        #     level=Qgis.Success,
        #     duration=10,
        # )
