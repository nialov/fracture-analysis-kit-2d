import logging

import pandas as pd
from qgis.core import QgsMessageLog

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
