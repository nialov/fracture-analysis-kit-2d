"""
Main module for the control of analysis and plotting.
"""
from qgis.core import QgsMessageLog, Qgis
from qgis.core import QgsTask, QgsApplication
import logging
from pathlib import Path

import config
from fracture_analysis_kit import analysis_and_plotting as taaq
from fracture_analysis_kit import qgis_tools as qgis_tools


def main_multi_target_area(layer_table_df, results_folder, analysis_name, group_names_cutoffs_df, set_df, choose_your_analyses):
    """
    Main method for firstly initializing data analysis, then starting data analysis,
    and then starting plotting of analysis results.
    Also initializes plotting directories, debugging methods and the plotting config parameters.

    :param layer_table_df: DataFrame with trace, branch, node, etc. vector layer data.
    :type layer_table_df: pandas.DataFrame
    :param results_folder: Path to folder in which plots_{analysis_name} folder will be built to
        and where plots will be saved to.
    :type results_folder: str
    :param analysis_name: Name for the analysis. Will be used in the plots_{analysis_name} folder name.
    :type analysis_name: str
    :param group_names_cutoffs_df: DataFrame with group name and cut-off data for both traces and branches.
    :type group_names_cutoffs_df: pandas.DataFrame
    :param set_df: DataFrame with set names and ranges.
    :type set_df: pandas.DataFrame
    :return: Returns analysis object.
    :rtype: taaq.MultiTargetAreaAnalysis
    """

    # SETUP PLOTTING DIRECTORIES
    QgsMessageLog.logMessage(message="Setting up plotting directories.", tag=f'{__name__}', level=Qgis.Info)
    plotting_directory = qgis_tools.plotting_directories(results_folder, analysis_name)

    # SETUP LOGGER
    logger = initialize_analysis_logging(plotting_directory)

    # SETUP CONFIG PARAMETERS
    config.n_ta = len(layer_table_df)
    config.n_g = len(group_names_cutoffs_df)
    config.ta_list = layer_table_df.Name.tolist()
    config.g_list = group_names_cutoffs_df.Group.tolist()

    # SAVE ANALYSIS SETTINGS AND INPUTS INTO LOGGER
    logger.info("Analysis Settings and Inputs")
    logger.info("-----------------------------------")
    logger.info(f"Layer table DataFrame:\n {layer_table_df.to_string()}")
    logger.info(f"Results folder:\n {results_folder}")
    logger.info(f"Analysis name:\n {analysis_name}")
    logger.info(f"Group names and Cut-offs DataFrame:\n {group_names_cutoffs_df.to_string()}")
    logger.info(f"Set DataFrame:\n {set_df.to_string()}")
    logger.info(f"Chosen analyses from config.py file:\n {choose_your_analyses}")

    # START __init__
    QgsMessageLog.logMessage(message="Initializing MultiTargetAnalysis.", tag=f'{__name__}', level=Qgis.Info)

    mta_analysis = taaq.MultiTargetAreaAnalysis(layer_table_df, plotting_directory, analysis_name,
                                                group_names_cutoffs_df, set_df, choose_your_analyses, logger)


    # Start analysis
    QgsMessageLog.logMessage(
        message="MultiTargetAnalysis analysis method started.", tag=f'{__name__}', level=Qgis.Info)

    mta_analysis.analysis()

    # Start plotting
    QgsMessageLog.logMessage(message="Multi Target Analysis plotting started.", tag=f'{__name__}', level=Qgis.Info)

    mta_analysis.plot_results()

    # Return analysis object
    return mta_analysis

def initialize_analysis_logging(plotting_directory):
    """
    Initializes a logger that collects all analysis statistics some of which are not drawn onto the finished
    plots.

    :param plotting_directory: The logger file is saved into the plotting_directory
    :type plotting_directory: str
    :return:
    :rtype:
    """
    filename = Path(plotting_directory) / Path("analysis_statistics.txt")
    if filename.exists():
        # Should not happen. But remove if exists. TODO: Add qgis message
        filename.unlink()
    # TODO: Is basicConfig needed?
    logging.basicConfig(filename=filename,
                        filemode="w+",
                        format="> %(message)s",
                        datefmt="%H:%M:%S'",
                        level=logging.INFO)

    logger = logging.getLogger("Analysis_Statistics")
    logger.setLevel(logging.DEBUG)
    filehandler = logging.FileHandler(filename)
    filehandler.setFormatter(
        logging.Formatter("%(message)s")
    )
    logger.addHandler(filehandler)

    logger.info("Analysis Statistics logfile initialized.")
    return logger

# def main_single_target_area(results_folder, name, trace_layer, branch_layer, node_layer, area_layer):
#     raise NotImplementedError('Not implemented.')
#     # # SETUP PLOTTING DIRECTORIES
#     # plotting_directory = qgis_tools.plotting_directories(results_folder, name)
#     # # START ANALYSIS FOR SINGLE TARGET AREA
#     # sta_analysis = taaq.TargetAreaAnalysis(plotting_directory, name, trace_layer, branch_layer, node_layer, area_layer)
#     # sta_analysis.plots()
#     # return sta_analysis


# def task_main_multi_target_area(table_df, results_folder, analysis_name, gnames_cutoffs_df, set_df):
#     task = QgsTask.fromFunction('Test test', main_multi_target_area_task, on_finished=task_completed
#                                 , table_df=table_df, results_folder=results_folder, analysis_name=analysis_name
#                                 , gnames_cutoffs_df=gnames_cutoffs_df, set_df=set_df)
#     # noinspection PyArgumentList
#     QgsMessageLog.logMessage(message=f'Task made {task.description()}', tag='TaskFromFunction', level=Qgis.Info)
#     QgsApplication.taskManager().addTask(task)
#     QgsMessageLog.logMessage(message=f'Added task to manager', tag='TaskFromFunction', level=Qgis.Info)


# def task_completed(exception, result):
#     """This is called when doSomething is finished.
#         Exception is not None if doSomething raises an exception.
#         result is the return value of doSomething."""
#
#     MESSAGE_CATEGORY = 'TaskFromFunction'
#
#     if exception is None:
#         if result is None:
#             QgsMessageLog.logMessage(message=
#                                      'Completed with no exception and no result ' \
#                                      '(probably manually canceled by the user)',
#                                      tag=MESSAGE_CATEGORY, level=Qgis.Warning)
#         else:
#             pass
#     else:
#         QgsMessageLog.logMessage(message="Exception: {}".format(exception),
#                                  tag=MESSAGE_CATEGORY, level=Qgis.Critical)
#         raise exception


# def main_multi_target_area_task(task, table_df, results_folder, analysis_name, gnames_cutoffs_df, set_df):
#     # noinspection PyArgumentList,PyArgumentList
#     QgsMessageLog.logMessage(message=f'Started task {task.description()}', tag='TaskFromFunction', level=Qgis.Info)
#
#     # SETUP PLOTTING DIRECTORIES
#     plotting_directory = qgis_tools.plotting_directories(results_folder, analysis_name)
#     # START init FOR MULTI TARGET AREA
#     mta_analysis = taaq.MultiTargetAreaAnalysis(table_df, plotting_directory, analysis_name, gnames_cutoffs_df, set_df)
#     # Start analysis
#     mta_analysis.analysis()
#     # Start plotting
#     task.setProgress(85)
#     mta_analysis.plot_results()
#     # Return analysis object
#     return mta_analysis


