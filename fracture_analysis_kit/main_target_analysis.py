import logging

import pandas as pd
from qgis.core import QgsMessageLog, Qgis
from qgis.core import QgsTask, QgsTaskManager, QgsApplication

from . import fracture_analysis_kit_qgis_tools as qgis_tools
from . import target_area_analysis_qgis as taaq


def main_single_target_area(results_folder, name, trace_layer, branch_layer, node_layer, area_layer, debug_logger):
    # SETUP PLOTTING DIRECTORIES
    plotting_directory = qgis_tools.plotting_directories(results_folder, name)
    # SETUP DEBUG LOGGER
    debug_logger.initialize_logging(plotting_directory)
    debug_logger.write_to_log('\n------DIRECTORIES MADE, DEBUG LOGGER INITIALIZED FOR RUN------\n')
    # START ANALYSIS FOR SINGLE TARGET AREA
    sta_analysis = taaq.TargetAreaAnalysis(plotting_directory, name, trace_layer, branch_layer, node_layer, area_layer,
                                           debug_logger)
    sta_analysis.plots()
    return sta_analysis

def task_main_multi_target_area(table_df, results_folder, analysis_name, gnames_cutoffs_df, set_df, debug_logger):

    task = QgsTask.fromFunction('Test test', main_multi_target_area_task, on_finished=task_completed
                                , table_df=table_df, results_folder=results_folder, analysis_name=analysis_name
                                , gnames_cutoffs_df=gnames_cutoffs_df, set_df=set_df, debug_logger=debug_logger)
    QgsMessageLog.logMessage(message=f'Task made {task.description()}', tag='TaskFromFunction', level=Qgis.Info)
    QgsApplication.taskManager().addTask(task)
    QgsMessageLog.logMessage(message=f'Added task to manager', tag='TaskFromFunction', level=Qgis.Info)

def task_completed(exception, result):
    """This is called when doSomething is finished.
        Exception is not None if doSomething raises an exception.
        result is the return value of doSomething."""

    MESSAGE_CATEGORY = 'TaskFromFunction'

    if exception is None:
        if result is None:
            QgsMessageLog.logMessage(message=
                'Completed with no exception and no result ' \
                '(probably manually canceled by the user)',
                tag=MESSAGE_CATEGORY, level=Qgis.Warning)
        else:
            pass
    else:
        QgsMessageLog.logMessage(message="Exception: {}".format(exception),
                                 tag=MESSAGE_CATEGORY, level=Qgis.Critical)
        raise exception

def main_multi_target_area_task(task, table_df, results_folder, analysis_name, gnames_cutoffs_df, set_df, debug_logger):
    QgsMessageLog.logMessage(message=f'Started task {task.description()}', tag='TaskFromFunction', level=Qgis.Info)
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.max_rows', 30)
    pd.set_option('display.max_columns', 500)
    # SETUP PLOTTING DIRECTORIES
    plotting_directory = qgis_tools.plotting_directories(results_folder, analysis_name)
    # SETUP DEBUG LOGGER
    debug_logger.initialize_logging(plotting_directory)

    # START init FOR MULTI TARGET AREA
    logger = logging.getLogger('logging_tool')
    logger.info('START OF INIT')
    mta_analysis = taaq.MultiTargetAreaAnalysis(table_df, plotting_directory, analysis_name, gnames_cutoffs_df, set_df)
    # Start analysis
    logger.info('START ANALYSIS')
    mta_analysis.analysis()
    # Start plotting
    logger.info('START PLOTTING')
    task.setProgress(85)
    mta_analysis.plot_results()
    logger.info('END PLOTTING')
    # Return analysis object
    return mta_analysis

def main_multi_target_area(table_df, results_folder, analysis_name, gnames_cutoffs_df, set_df, debug_logger):
    pd.set_option('display.max_colwidth', -1)
    pd.set_option('display.max_rows', 30)
    pd.set_option('display.max_columns', 500)
    # SETUP PLOTTING DIRECTORIES
    plotting_directory = qgis_tools.plotting_directories(results_folder, analysis_name)
    # SETUP DEBUG LOGGER
    debug_logger.initialize_logging(plotting_directory)

    # START init FOR MULTI TARGET AREA
    logger = logging.getLogger('logging_tool')
    logger.info('START OF INIT')
    mta_analysis = taaq.MultiTargetAreaAnalysis(table_df, plotting_directory, analysis_name, gnames_cutoffs_df, set_df)
    # Start analysis
    logger.info('START ANALYSIS')
    mta_analysis.analysis()
    # Start plotting
    logger.info('START PLOTTING')
    mta_analysis.plot_results()
    logger.info('END PLOTTING')
    # Return analysis object
    return mta_analysis


