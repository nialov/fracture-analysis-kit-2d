from pathlib import Path
import os
import shutil

from . import fracture_analysis_kit_qgis_tools as qgis_tools
# from .kit_resources import layers_to_pandas as lap
from .kit_resources import target_area as ta
from .kit_resources import multiple_target_areas as mta
from .kit_resources import templates

from . import logging_tool


# TODO: implement sets, more plotting
class TargetAreaAnalysis:
    def __init__(
            self, plotting_directory, name, trace_layer, branch_layer, node_layer, area_layer, debug_logger
    ):
        self.plotting_directory = plotting_directory
        self.name = name
        self.debug_logger = debug_logger

        self.trace_layer = trace_layer
        self.branch_layer = branch_layer
        self.node_layer = node_layer
        self.area_layer = area_layer

        # Initialize frames
        self.trace_frame = None
        self.branch_frame = None
        self.node_frame = None
        self.area_frame = None
        # Initialize target areas
        self.trace_ta = None
        self.branch_ta = None
        self.node_ta = None
        self.area_ta = None
        # Populate frames and target areas
        self.geopandafy()
        self.initialize_tas()

    def geopandafy(self):
        self.trace_frame = qgis_tools.df_to_gdf(df=qgis_tools.layer_to_df(self.trace_layer)[0],
                                         coord_system=qgis_tools.layer_to_df(self.trace_layer)[1])
        self.branch_frame = qgis_tools.df_to_gdf(df=qgis_tools.layer_to_df(self.branch_layer)[0],
                                          coord_system=qgis_tools.layer_to_df(self.branch_layer)[1])
        self.node_frame = qgis_tools.df_to_gdf(df=qgis_tools.layer_to_df(self.node_layer)[0],
                                        coord_system=qgis_tools.layer_to_df(self.node_layer)[1])
        self.area_frame = qgis_tools.df_to_gdf(df=qgis_tools.layer_to_df(self.area_layer)[0],
                                        coord_system=qgis_tools.layer_to_df(self.area_layer)[1])

    def initialize_tas(self):
        self.trace_ta = ta.TargetAreaLines(
            self.trace_frame,
            self.area_frame,
            code=self.name,
            cut_off=1.0,
            norm=1.0,
            filename=None,
            using_branches=False,
        )
        self.branch_ta = ta.TargetAreaLines(
            self.branch_frame,
            self.area_frame,
            code=self.name,
            cut_off=1.0,
            norm=1.0,
            filename=None,
            using_branches=True,
        )
        self.node_ta = ta.TargetAreaNodes(
            self.node_frame,
            code=self.name,
            filename=None,
        )

        # Calculates important attributes
        self.trace_ta.calc_attributes()
        self.branch_ta.calc_attributes()

        # Defines sets
        self.trace_ta.define_sets()
        self.branch_ta.define_sets()

    # Create folder structure for plots
    # TODO: use self.plotting_directories

    def plots(self):
        self.trace_ta.plot_length_distribution(save=True, savefolder=self.plotting_directory)
        self.branch_ta.calc_anisotropy()
        self.branch_ta.plot_anisotropy_styled(for_ax=False, ax=None, save=True, save_folder=self.plotting_directory)


class MultiTargetAreaAnalysis:

    def __init__(
            self, table_df, plotting_directory, analysis_name, gname_list, set_list, debug_logger
    ):
        self.set_list = set_list
        self.gname_list = gname_list
        self.table_df = table_df
        self.plotting_directory = plotting_directory
        self.analysis_name = analysis_name
        self.debug_logger = debug_logger

        debug_logger.write_to_log_time('Init of MultiTargetAnalysis start')

        self.table_df['Trace_frame'] = self.table_df['Trace'].apply(qgis_tools.layer_to_gdf)
        self.table_df['Branch_frame'] = self.table_df['Branch'].apply(qgis_tools.layer_to_gdf)
        self.table_df['Area_frame'] = self.table_df['Area'].apply(qgis_tools.layer_to_gdf)
        self.table_df['Node_frame'] = self.table_df['Node'].apply(qgis_tools.layer_to_gdf)

        debug_logger.write_to_log_time('Init of MultiTargetAnalysis analysis begin')

        self.analysis_traces = mta.MultiTargetAreaQGIS(self.table_df, self.gname_list, branches=False, debug_logger=self.debug_logger)
        self.analysis_branches = mta.MultiTargetAreaQGIS(self.table_df, self.gname_list, branches=True, debug_logger=self.debug_logger)
        
        # TRACE DATA SETUP
        self.analysis_traces.calc_attributes_for_all()
        self.analysis_traces.define_sets_for_all(self.set_list)
        # self.analysis_traces.calc_curviness_for_all()

        self.analysis_traces.unified()

        self.analysis_traces.create_setframes_for_all_unified()


        self.debug_logger.write_to_log_time(f'\nBefore xy_relations_all:{self.analysis_traces.uniframe.head()}')
        self.debug_logger.write_to_log_time(f'\nuniframe.iloc0:{self.analysis_traces.uniframe.iloc[0]}')
        self.debug_logger.write_to_log_time(f'\nuni_ld:{self.analysis_traces.uniframe.iloc[0].uni_ld}')
        self.debug_logger.write_to_log_time(f'\nuni_ld linef geom:{self.analysis_traces.uniframe.iloc[0].uni_ld.lineframe_main.geometry}')
        self.debug_logger.write_to_log_time(f'\nuni_ld linef geom0:{self.analysis_traces.uniframe.iloc[0].uni_ld.lineframe_main.geometry.iloc[0]}')

        self.analysis_traces.determine_xy_relations_all()
        self.analysis_traces.determine_xy_relations_unified()
        self.analysis_traces.gather_topology_parameters_unified()

        debug_logger.write_to_log_time('Init of MultiTargetAnalysis analysis traces done')

        # BRANCH DATA SETUP
        self.analysis_branches.calc_attributes_for_all()
        self.analysis_branches.define_sets_for_all(self.set_list)

        self.analysis_branches.unified()

        self.analysis_branches.create_setframes_for_all_unified()
        self.analysis_branches.gather_topology_parameters_unified()

        debug_logger.write_to_log_time('Init of MultiTargetAnalysis analysis end')

    def plot_results(self):
        self.debug_logger.write_to_log_time('Plotting start')

        # ___________________BRANCH DATA_______________________
        templates.styling_plots("branches")

        self.analysis_branches.plot_lengths_all(save=True, savefolder=self.plotting_directory + '/length_distributions/indiv/branches')
        self.analysis_branches.plot_lengths_unified()
        self.analysis_branches.plot_lengths_unified_combined(save=True, savefolder=self.plotting_directory + '/length_distributions/branches')

        # Length distribution predictions
        # for p in predict_with:
        #     self.analysis_branches.plot_lengths_unified_combined_predictions(
        #         save=True, savefolder=self.plotting_directory + '/length_distributions/branches/predictions', predict_with=p)
        # TODO: Fix azimuths plotting (redundant ellipse weighting)
        self.analysis_branches.plot_all_azimuths(big_plots=True, save=True
                                      , savefolder=self.plotting_directory + '/azimuths/branches')
        self.analysis_branches.plot_unified_azimuths(big_plots=True, save=True
                                          , savefolder=self.plotting_directory + '/azimuths/branches')
        self.analysis_branches.plot_all_xyi(save=True, savefolder=self.plotting_directory + "/xyi/individual")
        self.analysis_branches.plot_all_xyi_unified(save=True, savefolder=self.plotting_directory + '/xyi')
        self.analysis_branches.plot_topology_unified(save=True, savefolder=self.plotting_directory + '/topology/branches')
        self.analysis_branches.plot_hexbin_plot(save=True, savefolder=self.plotting_directory + '/hexbinplots')

        # ----------------unique for branches-------------------
        self.analysis_branches.plot_all_branch_ternary(
            save=True, savefolder=self.plotting_directory + "/branch_class"
        )
        self.analysis_branches.plot_all_branch_ternary_unified(
            save=True, savefolder=self.plotting_directory + "/branch_class"
        )
        self.analysis_branches.plot_anisotropy_all(save=True, savefolder=self.plotting_directory + '/anisotropy')
        self.analysis_branches.plot_anisotropy_unified(save=True, savefolder=self.plotting_directory + '/anisotropy')

        # __________________TRACE DATA______________________
        templates.styling_plots('traces')

        self.analysis_traces.plot_lengths_all(save=True, savefolder=self.plotting_directory + '/length_distributions/indiv/traces')
        self.analysis_traces.plot_lengths_unified()
        self.analysis_traces.plot_lengths_unified_combined(save=True, savefolder=self.plotting_directory + '/length_distributions/traces')

        # Length distribution predictions
        # for p in predict_with:
        #     self.analysis_traces.plot_lengths_unified_combined_predictions(
        #         save=True, savefolder=self.plotting_directory + '/length_distributions/traces/predictions', predict_with=p)

        self.analysis_traces.plot_all_azimuths(big_plots=True, save=True
                                     , savefolder=self.plotting_directory + '/azimuths/traces')
        self.analysis_traces.plot_unified_azimuths(big_plots=True, save=True
                                         , savefolder=self.plotting_directory + '/azimuths/traces')
        self.analysis_traces.plot_topology_unified(save=True, savefolder=self.plotting_directory + '/topology/traces')
        self.analysis_traces.plot_hexbin_plot(save=True, savefolder=self.plotting_directory + '/hexbinplots')

        # ---------------unique for traces-------------------
        self.analysis_traces.plot_xy_age_relations_all(save=True, savefolder=self.plotting_directory + '/age_relations/indiv')
        self.analysis_traces.plot_xy_age_relations_unified(save=True, savefolder=self.plotting_directory + '/age_relations')

        # TODO: big plot for violins + legend?
        # self.analysis_traces.plot_curviness_for_unified(violins=True, save=True, savefolder=self.plotting_directory + '/curviness/traces')

        self.debug_logger.write_to_log_time('Plotting end')
        
        
        



