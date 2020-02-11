import logging


from . import fracture_analysis_kit_qgis_tools as qgis_tools
from .kit_resources import multiple_target_areas as mta
# from .kit_resources import layers_to_pandas as lap
from .kit_resources import target_area as ta
from .. import config


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
            name=self.name,
            group=self.name,
            cut_off=1.0,
            using_branches=False,
        )
        self.branch_ta = ta.TargetAreaLines(
            self.branch_frame,
            self.area_frame,
            name=self.name,
            group=self.name,
            cut_off=1.0,
            using_branches=True,
        )
        self.node_ta = ta.TargetAreaNodes(
            self.node_frame,
            name=self.name,
            group=self.name,
        )

        # Calculates important attributes
        self.trace_ta.calc_attributes()
        self.branch_ta.calc_attributes()

        # Defines sets
        self.trace_ta.define_sets()
        self.branch_ta.define_sets()

    # Create folder structure for plots


    def plots(self):
        self.trace_ta.plot_length_distribution(save=True, savefolder=self.plotting_directory)
        self.branch_ta.calc_anisotropy()
        self.branch_ta.plot_anisotropy_styled(for_ax=False, ax=None, save=True, save_folder=self.plotting_directory)


class MultiTargetAreaAnalysis:

    def __init__(
            self, table_df, plotting_directory, analysis_name, gnames_cutoffs_df, set_df
    ):
        self.logger = logging.getLogger('logging_tool')
        self.set_df = set_df
        self.gnames_cutoffs_df = gnames_cutoffs_df
        self.table_df = table_df
        self.plotting_directory = plotting_directory
        self.analysis_name = analysis_name
        self.analysis_traces = None
        self.analysis_branches = None

        # Convert QGIS-layers to GeoDataFrames
        self.table_df['Trace_frame'] = self.table_df['Trace'].apply(qgis_tools.layer_to_gdf)
        self.table_df['Branch_frame'] = self.table_df['Branch'].apply(qgis_tools.layer_to_gdf)
        self.table_df['Area_frame'] = self.table_df['Area'].apply(qgis_tools.layer_to_gdf)
        self.table_df['Node_frame'] = self.table_df['Node'].apply(qgis_tools.layer_to_gdf)

    def analysis(self):
        # DEBUG
        # self.table_df = self.table_df.drop(columns=['Trace', 'Branch', 'Area', 'Node'])
        self.logger.info('CREATING MultiTargetAreaQGIS FOR TRACES AND BRANCHES')

        self.analysis_traces = mta.MultiTargetAreaQGIS(self.table_df, self.gnames_cutoffs_df, branches=False)
        # Bar at 25

        self.analysis_branches = mta.MultiTargetAreaQGIS(self.table_df, self.gnames_cutoffs_df, branches=True)
        # Bar at 45

        # TRACE DATA SETUP
        self.logger.info('CALC ATTRIBUTES TRACES')
        self.analysis_traces.calc_attributes_for_all()

        self.analysis_traces.define_sets_for_all(self.set_df)

        # self.analysis_traces.calc_curviness_for_all()
        self.logger.info('UNIFIED TRACES')
        self.analysis_traces.unified()

        # self.logger.info('UNIFIED SETFRAMES')
        # TODO: Check setframes
        # self.analysis_traces.create_setframes_for_all_unified()

        self.analysis_traces.gather_topology_parameters(unified=False)
        self.analysis_traces.gather_topology_parameters(unified=True)

        # Cross-cutting and abutting relationships
        self.analysis_traces.determine_crosscut_abutting_relationships(unified=False)
        self.analysis_traces.determine_crosscut_abutting_relationships(unified=True)

        # BRANCH DATA SETUP
        self.analysis_branches.calc_attributes_for_all()

        self.analysis_branches.define_sets_for_all(self.set_df)

        self.analysis_branches.unified()

        self.analysis_branches.gather_topology_parameters(unified=False)
        self.analysis_branches.gather_topology_parameters(unified=True)

        self.logger.info('END ANALYSIS in analysis()')
        # Bar at 85

    def plot_results(self):
        self.logger.info('START OF PLOTTING RESULTS')
        self.logger.info('__________________BRANCH DATA PLOTTING START______________________')

        # ___________________BRANCH DATA_______________________
        config.styling_plots("branches")
        # Length distributions
        self.analysis_branches.plot_lengths(unified=False, save=True,
                                            savefolder=self.plotting_directory + '/length_distributions/indiv/branches')
        self.analysis_branches.plot_lengths(unified=True, save=True,
                                            savefolder=self.plotting_directory + '/length_distributions/branches')

        # TODO: Length distribution predictions
        # for p in predict_with:
        #     self.analysis_branches.plot_lengths_unified_combined_predictions(
        #         save=True, savefolder=self.plotting_directory + '/length_distributions/branches/predictions', predict_with=p)

        # Azimuths
        self.analysis_branches.plot_azimuths_weighted(unified=False, save=True,
                                                      savefolder=self.plotting_directory + '/azimuths/indiv')
        self.analysis_branches.plot_azimuths_weighted(unified=True, save=True,
                                                      savefolder=self.plotting_directory + '/azimuths')
        # XYI
        # self.analysis_branches.plot_xyi(unified=False, save=True,
        #                                 savefolder=self.plotting_directory + "/xyi/individual")
        # self.analysis_branches.plot_xyi(unified=True, save=True,
        #                                 savefolder=self.plotting_directory + "/xyi")
        self.analysis_branches.plot_xyi_ternary(unified=False, save=True,
                                        savefolder=self.plotting_directory + "/xyi")
        self.analysis_branches.plot_xyi_ternary(unified=True, save=True,
                                                savefolder=self.plotting_directory + "/xyi")

        # Topo parameters
        self.analysis_branches.plot_topology(unified=False, save=True,
                                             savefolder=self.plotting_directory + '/topology/branches')
        self.analysis_branches.plot_topology(unified=True, save=True,
                                             savefolder=self.plotting_directory + '/topology/branches')
        # Hexbinplots
        self.analysis_branches.plot_hexbin_plot(unified=False, save=True,
                                                savefolder=self.plotting_directory + '/hexbinplots')
        self.analysis_branches.plot_hexbin_plot(unified=True, save=True,
                                                savefolder=self.plotting_directory + '/hexbinplots')

        # ----------------unique for branches-------------------
        # Branch Classification ternary plot
        self.analysis_branches.plot_branch_ternary(unified=False,
                                                   save=True, savefolder=self.plotting_directory + "/branch_class"
                                                   )
        self.analysis_branches.plot_branch_ternary(unified=True,
                                                   save=True, savefolder=self.plotting_directory + "/branch_class"
                                                   )

        # Anisotropy
        self.analysis_branches.plot_anisotropy(unified=False, save=True,
                                               savefolder=self.plotting_directory + '/anisotropy/indiv')
        self.analysis_branches.plot_anisotropy(unified=True, save=True,
                                               savefolder=self.plotting_directory + '/anisotropy')

        self.logger.info('__________________TRACE DATA PLOTTING START______________________')

        # __________________TRACE DATA______________________
        config.styling_plots('traces')

        self.analysis_traces.plot_lengths(unified=False, save=True,
                                          savefolder=self.plotting_directory + '/length_distributions/indiv/traces')
        self.analysis_traces.plot_lengths(unified=True, save=True,
                                          savefolder=self.plotting_directory + '/length_distributions/traces')

        # Length distribution predictions
        # for p in predict_with:
        #     self.analysis_traces.plot_lengths_unified_combined_predictions(
        #         save=True, savefolder=self.plotting_directory + '/length_distributions/traces/predictions', predict_with=p)

        # Azimuths
        self.analysis_traces.plot_azimuths_weighted(unified=False, save=True,
                                                      savefolder=self.plotting_directory + '/azimuths/indiv')
        self.analysis_traces.plot_azimuths_weighted(unified=True, save=True,
                                                      savefolder=self.plotting_directory + '/azimuths')
        # self.analysis_traces.plot_azimuths(unified=False, rose_type='equal-radius', save=True
        #                                    , savefolder=self.plotting_directory + '/azimuths/equal_radius/traces')
        # self.analysis_traces.plot_azimuths(unified=True, rose_type='equal-radius', save=True
        #                                    , savefolder=self.plotting_directory + '/azimuths/equal_radius/traces')
        # self.analysis_traces.plot_azimuths(unified=False, rose_type='equal-area', save=True
        #                                    , savefolder=self.plotting_directory + '/azimuths/equal_area/traces')
        # self.analysis_traces.plot_azimuths(unified=True, rose_type='equal-area', save=True
        #                                    , savefolder=self.plotting_directory + '/azimuths/equal_area/traces')
        # Topo parameters
        self.analysis_traces.plot_topology(unified=False, save=True,
                                           savefolder=self.plotting_directory + '/topology/traces')
        self.analysis_traces.plot_topology(unified=True, save=True,
                                           savefolder=self.plotting_directory + '/topology/traces')
        # Hexbinplots
        self.analysis_traces.plot_hexbin_plot(unified=False, save=True,
                                              savefolder=self.plotting_directory + '/hexbinplots')
        self.analysis_traces.plot_hexbin_plot(unified=True, save=True,
                                              savefolder=self.plotting_directory + '/hexbinplots')

        # ---------------unique for traces-------------------
        # TODO: Fix for age relations single ax, put data into multiple images?
        # TODO: Fix whole age analysis

        # Cross-cutting and abutting relationships
        self.logger.info('Plotting crosscutting and abutting rels')
        self.analysis_traces.plot_crosscut_abutting_relationships(unified=False, save=True, savefolder=self.plotting_directory + '/age_relations/indiv')
        self.analysis_traces.plot_crosscut_abutting_relationships(unified=True, save=True, savefolder=self.plotting_directory + '/age_relations')
        self.logger.info('Plotting crosscutting and abutting rels ENDED')
        # logger.info(f'self.table_df:\n\n{self.table_df}')
        #
        # self.logger.info(f'Shape of self.table_df: {self.table_df.shape}')
        # self.logger.info(f'Len of self.table_df: {len(self.table_df)}')
        #
        # if self.table_df.shape[0] > 1:
        #     self.analysis_traces.plot_xy_age_relations_all(save=True, savefolder=self.plotting_directory + '/age_relations/indiv')
        #     self.analysis_traces.plot_xy_age_relations_unified(save=True, savefolder=self.plotting_directory + '/age_relations')

        # TODO: big plot for violins + legend?
        # self.analysis_traces.plot_curviness_for_unified(violins=True, save=True, savefolder=self.plotting_directory + '/curviness/traces')

        self.logger.info('Plotting end!')
