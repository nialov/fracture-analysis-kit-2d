"""
Handles analysis and plotting using a MultiTargetAreaAnalysis class. Analysis (i.e. heavy calculations)
and plotting have been separated into two different methods.
"""
from qgis.core import QgsMessageLog, Qgis
import config
from fracture_analysis_kit import qgis_tools as qgis_tools, multiple_target_areas as mta


class MultiTargetAreaAnalysis:

    def __init__(
            self, layer_table_df, plotting_directory, analysis_name, group_names_cutoffs_df, set_df
    ):
        """
        Initializes data and user inputs for the analysis and plotting. Converts QGIS-layers to geopandas GeoDataFrames.

        :param layer_table_df: DataFrame with user inputted vector layer data and unique names for target areas.
        :type layer_table_df: pandas.DataFrame
        :param plotting_directory: Folder to plot results to.
        :type plotting_directory: str
        :param analysis_name: Name for the whole analysis.
        :type analysis_name: str
        :param group_names_cutoffs_df: DataFrame with group names and corresponding cut-offs for traces and branches.
        :type group_names_cutoffs_df: pandas.DataFrame
        :param set_df: DataFrame with set data.
        :type set_df: pandas.DataFrame
        """
        self.set_df = set_df
        self.group_names_cutoffs_df = group_names_cutoffs_df
        self.layer_table_df = layer_table_df
        self.plotting_directory = plotting_directory
        self.analysis_name = analysis_name
        self.analysis_traces = None
        self.analysis_branches = None

        # Convert QGIS-layers to GeoDataFrames
        # and drop unused columns to free memory

        QgsMessageLog.logMessage(message=f"Converting QGIS trace layers to GeoDataFrames"
                                 , tag=f'{__name__}', level=Qgis.Info)
        self.layer_table_df['Trace_frame'] = self.layer_table_df['Trace'].apply(qgis_tools.layer_to_gdf)
        self.layer_table_df = self.layer_table_df.drop("Trace", 1)

        QgsMessageLog.logMessage(message=f"Converting QGIS branch layers to GeoDataFrames"
                                 , tag=f'{__name__}', level=Qgis.Info)
        self.layer_table_df['Branch_frame'] = self.layer_table_df['Branch'].apply(qgis_tools.layer_to_gdf)
        self.layer_table_df = self.layer_table_df.drop("Branch", 1)

        QgsMessageLog.logMessage(message=f"Converting QGIS area layers to GeoDataFrames"
                                 , tag=f'{__name__}', level=Qgis.Info)

        self.layer_table_df['Area_frame'] = self.layer_table_df['Area'].apply(qgis_tools.layer_to_gdf)
        self.layer_table_df = self.layer_table_df.drop("Area", 1)

        QgsMessageLog.logMessage(message=f"Converting QGIS node layers to GeoDataFrames"
                                 , tag=f'{__name__}', level=Qgis.Info)

        self.layer_table_df['Node_frame'] = self.layer_table_df['Node'].apply(qgis_tools.layer_to_gdf)
        self.layer_table_df = self.layer_table_df.drop("Node", 1)

        QgsMessageLog.logMessage(message=f"Checking if cross-cutting and abutting relationships are determined."
                                 , tag=f'{__name__}', level=Qgis.Info)
        # Check if cross-cutting and abutting relationships can be determined
        # TODO: Also check if sets actually exist in lines...
        if len(self.set_df) < 2:
            self.determine_relationships = False
        else:
            self.determine_relationships = True

    def analysis(self):
        """
        Method that runs analysis i.e. heavy calculations for trace, branch and node data.
        """
        # DEBUG
        # self.layer_table_df = self.layer_table_df.drop(columns=['Trace', 'Branch', 'Area', 'Node'])

        QgsMessageLog.logMessage(
            message="Initializing MultiTargetAreaQGIS objects for traces and branches."
            , tag=f'{__name__}', level=Qgis.Info)

        self.analysis_traces = mta.MultiTargetAreaQGIS(self.layer_table_df, self.group_names_cutoffs_df, branches=False)
        # Bar at 25

        self.analysis_branches = mta.MultiTargetAreaQGIS(self.layer_table_df, self.group_names_cutoffs_df,
                                                         branches=True)
        # Bar at 45
        QgsMessageLog.logMessage(
            message="Calculating attributes for traces.", tag=f'{__name__}', level=Qgis.Info)
        # TRACE DATA SETUP
        self.analysis_traces.calc_attributes_for_all()

        QgsMessageLog.logMessage(
            message="Defining sets for traces.", tag=f'{__name__}', level=Qgis.Info)

        self.analysis_traces.define_sets_for_all(self.set_df)

        QgsMessageLog.logMessage(
            message="Defining grouping for traces.", tag=f'{__name__}', level=Qgis.Info)

        # self.analysis_traces.calc_curviness_for_all()
        self.analysis_traces.unified()

        # TODO: Check setframes
        # self.analysis_traces.create_setframes_for_all_unified()

        QgsMessageLog.logMessage(
            message="Gathering topological parameters for traces."
            , tag=f'{__name__}', level=Qgis.Info)

        self.analysis_traces.gather_topology_parameters(unified=False)
        self.analysis_traces.gather_topology_parameters(unified=True)

        # Cross-cutting and abutting relationships
        QgsMessageLog.logMessage(
            message="Determining cross-cutting and abutting relationships for traces."
            , tag=f'{__name__}', level=Qgis.Info)
        if self.determine_relationships:
            self.analysis_traces.determine_crosscut_abutting_relationships(unified=False)
            self.analysis_traces.determine_crosscut_abutting_relationships(unified=True)

        # BRANCH DATA SETUP
        QgsMessageLog.logMessage(
            message="Calculating attributes for branches.", tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.calc_attributes_for_all()

        QgsMessageLog.logMessage(
            message="Defining sets for branches.", tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.define_sets_for_all(self.set_df)

        QgsMessageLog.logMessage(
            message="Defining grouping for branches.", tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.unified()

        QgsMessageLog.logMessage(
            message="Gathering topological parameters for branches."
            , tag=f'{__name__}', level=Qgis.Info)

        self.analysis_branches.gather_topology_parameters(unified=False)
        self.analysis_branches.gather_topology_parameters(unified=True)

        QgsMessageLog.logMessage(
            message="Defining anisotropy of connectivity for branches."
            , tag=f'{__name__}', level=Qgis.Info)

        # Anisotropy
        self.analysis_branches.calc_anisotropy(unified=False)
        self.analysis_branches.calc_anisotropy(unified=True)

    def plot_results(self):
        """
        Method that runs plotting based on analysis results for trace, branch and node data.
        """
        # ___________________BRANCH DATA_______________________
        config.styling_plots("branches")
        # Length distributions
        QgsMessageLog.logMessage(
            message="Plotting branch length distributions."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.plot_lengths(unified=False, save=True,
                                            savefolder=self.plotting_directory + '/length_distributions/indiv/branches')
        self.analysis_branches.plot_lengths(unified=True, save=True,
                                            savefolder=self.plotting_directory + '/length_distributions/branches')

        # TODO: Length distribution predictions
        # for p in predict_with:
        #     self.analysis_branches.plot_lengths_unified_combined_predictions(
        #         save=True, savefolder=self.plotting_directory + '/length_distributions/branches/predictions', predict_with=p)

        # Azimuths
        QgsMessageLog.logMessage(
            message="Plotting azimuths for branches."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.plot_azimuths_weighted(unified=False, save=True,
                                                      savefolder=self.plotting_directory + '/azimuths/indiv')
        self.analysis_branches.plot_azimuths_weighted(unified=True, save=True,
                                                      savefolder=self.plotting_directory + '/azimuths')
        # XYI
        QgsMessageLog.logMessage(
            message="Plotting XYI for branches."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.plot_xyi_ternary(unified=False, save=True,
                                                savefolder=self.plotting_directory + "/xyi")
        self.analysis_branches.plot_xyi_ternary(unified=True, save=True,
                                                savefolder=self.plotting_directory + "/xyi")

        # Topo parameters
        QgsMessageLog.logMessage(
            message="Plotting topology for branches."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.plot_topology(unified=False, save=True,
                                             savefolder=self.plotting_directory + '/topology/branches')
        self.analysis_branches.plot_topology(unified=True, save=True,
                                             savefolder=self.plotting_directory + '/topology/branches')
        # Hexbinplots
        QgsMessageLog.logMessage(
            message="Plotting hexbinplots for branches."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.plot_hexbin_plot(unified=False, save=True,
                                                savefolder=self.plotting_directory + '/hexbinplots')
        self.analysis_branches.plot_hexbin_plot(unified=True, save=True,
                                                savefolder=self.plotting_directory + '/hexbinplots')

        # ----------------unique for branches-------------------
        # Branch Classification ternary plot
        QgsMessageLog.logMessage(
            message="Plotting branch classification plot for branches."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.plot_branch_ternary(unified=False,
                                                   save=True, savefolder=self.plotting_directory + "/branch_class"
                                                   )
        self.analysis_branches.plot_branch_ternary(unified=True,
                                                   save=True, savefolder=self.plotting_directory + "/branch_class"
                                                   )

        # Anisotropy
        QgsMessageLog.logMessage(
            message="Plotting anisotropy of connectivity for branches."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_branches.plot_anisotropy(unified=False, save=True,
                                               savefolder=self.plotting_directory + '/anisotropy/indiv')
        self.analysis_branches.plot_anisotropy(unified=True, save=True,
                                               savefolder=self.plotting_directory + '/anisotropy')

        # __________________TRACE DATA______________________
        config.styling_plots('traces')
        QgsMessageLog.logMessage(
            message="Plotting trace length distributions."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_traces.plot_lengths(unified=False, save=True,
                                          savefolder=self.plotting_directory + '/length_distributions/indiv/traces')
        self.analysis_traces.plot_lengths(unified=True, save=True,
                                          savefolder=self.plotting_directory + '/length_distributions/traces')

        # Length distribution predictions
        # for p in predict_with:
        #     self.analysis_traces.plot_lengths_unified_combined_predictions(
        #         save=True, savefolder=self.plotting_directory + '/length_distributions/traces/predictions', predict_with=p)

        # Azimuths
        QgsMessageLog.logMessage(
            message="Plotting azimuths for traces."
            , tag=f'{__name__}', level=Qgis.Info)
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
        QgsMessageLog.logMessage(
            message="Plotting topology for traces."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_traces.plot_topology(unified=False, save=True,
                                           savefolder=self.plotting_directory + '/topology/traces')
        self.analysis_traces.plot_topology(unified=True, save=True,
                                           savefolder=self.plotting_directory + '/topology/traces')
        # Hexbinplots
        QgsMessageLog.logMessage(
            message="Plotting hexbinplots for traces."
            , tag=f'{__name__}', level=Qgis.Info)
        self.analysis_traces.plot_hexbin_plot(unified=False, save=True,
                                              savefolder=self.plotting_directory + '/hexbinplots')
        self.analysis_traces.plot_hexbin_plot(unified=True, save=True,
                                              savefolder=self.plotting_directory + '/hexbinplots')

        # ---------------unique for traces-------------------

        # Cross-cutting and abutting relationships
        # TODO: Implement Markov chain analysis?
        # Fracture overprinting history using Markov chain analysis:
        # Windsor-Kennetcook subbasin, Maritimes Basin, Canada
        if self.determine_relationships:
            QgsMessageLog.logMessage(
                message="Plotting cross-cutting and abutting relationships for traces."
                , tag=f'{__name__}', level=Qgis.Info)
            self.analysis_traces.plot_crosscut_abutting_relationships(unified=False, save=True,
                                                                      savefolder=self.plotting_directory + '/age_relations/indiv')
            self.analysis_traces.plot_crosscut_abutting_relationships(unified=True, save=True,
                                                                      savefolder=self.plotting_directory + '/age_relations')
        #
        # if self.layer_table_df.shape[0] > 1:
        #     self.analysis_traces.plot_xy_age_relations_all(save=True, savefolder=self.plotting_directory + '/age_relations/indiv')
        #     self.analysis_traces.plot_xy_age_relations_unified(save=True, savefolder=self.plotting_directory + '/age_relations')

        # TODO: Curviness
        # self.analysis_traces.plot_curviness_for_unified(violins=True, save=True, savefolder=self.plotting_directory + '/curviness/traces')
