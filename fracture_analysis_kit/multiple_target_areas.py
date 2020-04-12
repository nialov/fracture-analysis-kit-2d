"""
Handles multiple given target areas and makes groups of them based on user inputs using a MultiTargetAreaQGIS class.
MultiTargetAreaQGIS-objects are made separately for trace and branch data. Both contain the same node data.
"""

# Python Windows co-operation imports
from pathlib import Path
# Math and analysis imports
# Plotting imports
# DataFrame analysis imports
from textwrap import wrap

import geopandas as gpd
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shapely
import sklearn.metrics as sklm
import ternary
import itertools
from qgis.core import QgsMessageLog, Qgis

# Own code imports
import config
from fracture_analysis_kit import target_area as ta, tools


# from . import target_area as ta
# from . import tools
# from ... import config


# import kit_resources.templates as templates  # Contains plotting templates
# import kit_resources.tools as tools  # Main tool/helper module

# Old class


class MultiTargetAreaQGIS:

    def __init__(self, table_df, gnames_cutoffs_df, branches):
        """
        Class for operations with multiple target areas. Handles grouping, analysis and plotting of both individual
        target areas and grouped data.

        :param table_df: DataFrame with user inputs
        :type table_df: pd.DataFrame
        :param gnames_cutoffs_df: Group names and cut-offs from user input
        :type gnames_cutoffs_df: pd.DataFrame
        :param branches: Branches or traces
        :type branches: bool
        """
        self.group_names_cutoffs_df = gnames_cutoffs_df
        self.groups = gnames_cutoffs_df.Group.tolist()
        # self.codes = group_names_cutoffs_df
        self.table_df = table_df

        self.using_branches = branches

        self.df = pd.DataFrame(columns=['name', 'lineframe', 'areaframe', 'nodeframe', 'group', 'cut_off_length'])
        # Assign None to later initialized attributes
        # TODO: Add DF columns here?
        self.set_ranges_list = None
        self.set_df = None
        self.uniframe = None
        self.df_lineframe_main_concat = None
        self.df_lineframe_main_cut_concat = None
        self.uniframe_lineframe_main_concat = None
        self.uniframe_lineframe_main_cut_concat = None
        self.uni_left, self.uni_right, self.uni_top, self.uni_bottom = None, None, None, None
        self.relations_set_counts = None
        self.xy_relations_frame = None
        self.xy_relations_frame_indiv = None
        self.relations_set_counts = None
        self.df_topology_concat = None
        self.uniframe_topology_concat = None
        self.relations_set_counts_indiv = None
        self.relations_df = None
        self.unified_relations_df = None

        # Iterate over all target areas
        for _, row in table_df.iterrows():
            name = row.Name
            if self.using_branches:
                lineframe = row.Branch_frame
            else:
                lineframe = row.Trace_frame
            areaframe = row.Area_frame
            nodeframe = row.Node_frame
            group = row.Group

            # Cut-off for group
            cut_offs = self.group_names_cutoffs_df.loc[self.group_names_cutoffs_df.Group == group]
            assert len(cut_offs.CutOffBranches) == 1
            cut_off_length = cut_offs.CutOffBranches.iloc[0] if self.using_branches else cut_offs.CutOffTraces.iloc[0]

            try:
                cut_off_length = float(cut_off_length)
            except TypeError:
                QgsMessageLog.logMessage(message=
                                         f'Cut-off value was an iterable or not convertible to float. CutOff value: {cut_off_length}'
                                         f'Type: {str(type(cut_off_length))}', tag=__name__, level=Qgis.Critical)
                raise

            # Initialize DataFrames with additional columns
            lineframe['azimu'] = lineframe.geometry.apply(tools.calc_azimu)
            lineframe['halved'] = lineframe.azimu.apply(tools.azimu_half)
            nodeframe['c'] = nodeframe.Class.apply(str)

            # Change MultiLineStrings to LineStrings. Delete unmergeable MultiLineStrings. A trace should be mergeable.
            if isinstance(lineframe.geometry.iloc[0], shapely.geometry.MultiLineString):
                non_mergeable_idx = []
                for idx, srs in lineframe.iterrows():
                    try:
                        lineframe.geometry.iloc[idx] = shapely.ops.linemerge(srs.geometry)
                    except ValueError:
                        non_mergeable_idx.append(idx)
                    # Should be LineString if mergeable. If not:
                    if isinstance(lineframe.geometry.iloc[idx], shapely.geometry.MultiLineString):
                        non_mergeable_idx.append(idx)
                # Drop non-mergeable
                lineframe = lineframe.drop(index=non_mergeable_idx)

            if self.using_branches:
                lineframe['c'] = lineframe.Class.apply(str)
                lineframe['connection'] = lineframe.Connection.apply(str)

            # Append to DataFrame
            self.df = self.df.append({'name': name, 'lineframe': lineframe, 'areaframe': areaframe
                                         , 'nodeframe': nodeframe, 'group': group, 'cut_off_length': cut_off_length},
                                     ignore_index=True)

        self.df['TargetAreaLines'] = self.df.apply(
            lambda x: tools.construct_length_distribution_base(x['lineframe'], x['areaframe'], x['name'], x['group'],
                                                               x['cut_off_length'], self.using_branches),
            axis=1)
        self.df['TargetAreaNodes'] = self.df.apply(
            lambda x: tools.construct_node_data_base(x['nodeframe'], x['name'], x['group']), axis=1)

    def calc_attributes_for_all(self):
        """
        Calculates attributes for all target areas.
        """
        for idx, row in self.df.iterrows():
            row['TargetAreaLines'].calc_attributes()
        self.df_lineframe_main_concat = pd.concat([srs.lineframe_main for srs in self.df.TargetAreaLines],
                                                  sort=True)
        self.df_lineframe_main_cut_concat = pd.concat([srs.lineframe_main_cut for srs in self.df.TargetAreaLines],
                                                      sort=True)

    def define_sets_for_all(self, set_df):
        """
        Categorizes data based on azimuth to sets.

        :param set_df: DataFrame with sets. Columns: "Set", "SetLimits"
        :type set_df: DataFrame
        """
        self.set_df = set_df
        for idx, row in self.df.iterrows():
            row['TargetAreaLines'].define_sets(set_df)

    def calc_curviness_for_all(self, use_branches_anyway=False):
        if use_branches_anyway:
            pass
        elif self.using_branches:
            raise Exception('Not recommended for branch data.')
        for idx, row in self.df.iterrows():
            row['TargetAreaLines'].calc_curviness()

    def unified(self):
        """
        Creates new datasets (TargetAreaLines + TargetAreaNodes for each group) based on groupings by user.

        :raise ValueError: When there are groups without any target areas.
        """
        uniframe = pd.DataFrame(
            columns=['TargetAreaLines', 'TargetAreaNodes', 'group', 'name', 'uni_ld_area', 'cut_off_length'])
        for idx, group in enumerate(self.groups):
            frame = self.df.loc[self.df['group'] == group]

            if len(frame) > 0:
                # Cut-off from user input table.
                if self.using_branches:
                    cut_off_length = \
                        self.group_names_cutoffs_df.loc[self.group_names_cutoffs_df.Group == group].CutOffBranches.iloc[
                            0]
                else:
                    cut_off_length = \
                        self.group_names_cutoffs_df.loc[self.group_names_cutoffs_df.Group == group].CutOffTraces.iloc[0]
                # cut_off = frame.cut_off.iloc[0]

                # Hunting possible bugs:
                assert len(
                    self.group_names_cutoffs_df.loc[self.group_names_cutoffs_df.Group == group].CutOffTraces) == 1
                assert len(
                    self.group_names_cutoffs_df.loc[self.group_names_cutoffs_df.Group == group].CutOffBranches) == 1

                unif_ld_main = tools.unify_lds(frame.TargetAreaLines.tolist(), group, cut_off_length)
                unif_ld_main.calc_attributes()
                uni_ld_area = gpd.GeoDataFrame(pd.concat(frame.areaframe.tolist(), ignore_index=True))
                unif_nd_main = tools.unify_nds(frame.TargetAreaNodes.tolist(), group)
                uniframe = uniframe.append(
                    {'TargetAreaLines': unif_ld_main, 'TargetAreaNodes': unif_nd_main, 'group': group, 'name': group,
                     'uni_ld_area': uni_ld_area, 'cut_off_length': cut_off_length},
                    ignore_index=True)
            else:
                raise ValueError('There are groups without any target areas.'
                                 f'Group name: {group}')

        # uniframe = tools.norm_unified(uniframe)
        self.uniframe = uniframe
        # AIDS FOR PLOTTING:
        self.uniframe_lineframe_main_concat = pd.concat([srs.lineframe_main for srs in self.uniframe.TargetAreaLines],
                                                        sort=True)
        self.uniframe_lineframe_main_cut_concat = pd.concat(
            [srs.lineframe_main_cut for srs in self.uniframe.TargetAreaLines],
            sort=True)
        self.uni_left, self.uni_right = tools.calc_xlims(self.uniframe_lineframe_main_concat)
        self.uni_top, self.uni_bottom = tools.calc_ylims(self.uniframe_lineframe_main_concat)

    def plot_curviness_for_unified(self, violins=False, save=False, savefolder=''):
        if violins:
            for idx, row in self.uniframe.iterrows():
                row['TargetAreaLines'].plot_curviness_violins()
                if save:
                    savename = Path(savefolder + '/{}_curviness_violin'.format(row['name']))
                    plt.savefig(savename, dpi=150)
        else:
            for idx, row in self.uniframe.iterrows():
                row['TargetAreaLines'].plot_curviness()
                if save:
                    savename = Path(savefolder + '/{}_curviness_box'.format(row['name']))
                    plt.savefig(savename, dpi=150)

    def create_setframes_for_all_unified(self):
        for idx, row in self.uniframe.iterrows():
            row['TargetAreaLines'].create_setframes()

    def plot_length_fit_cut_ax(self, ax, unified: bool):
        """
        Plots the numerical power-law fit to a cut length distribution to a given ax.

        :param ax: ax to plot to.
        :type ax: matplotlib.axes.Axes
        :param unified: Whether to plot for target area or grouped data.
        :type unified: bool
        :raise ValueError: When there are too many values from np.polyfit i.e. values != 2.
        """

        def create_text(lineframe_for_text, ax_for_text):
            """
            Sub-method to create Texts based on the length distribution DataFrame to a given ax.'

            :param lineframe_for_text: Length distribution.
            :type lineframe_for_text: pandas.DataFrame | geopandas.GeoDataFrame
            :param ax_for_text: Ax to create texts to.
            :type ax_for_text: matplotlib.axes.Axes
            """
            msle = sklm.mean_squared_log_error(lineframe_for_text.y.values, lineframe_for_text.y_fit.values)
            r2score = sklm.r2_score(lineframe_for_text.y.values, lineframe_for_text.y_fit.values)

            text = f'$Exponent = {str(np.round(m, 2))}$' \
                   + f'\n$Constant = {str(np.round(c, 2))}$' \
                   + f'\n$MSLE = {str(np.round(msle, 3))}$' \
                   + f'\n$R^2 = {str(np.round(r2score, 5))}$'

            props = dict(boxstyle='square', facecolor='linen', alpha=1, pad=0.4)

            ax_for_text.text(1.3, 0.6, text, transform=ax_for_text.transAxes
                             , bbox=props, style='italic', ha='center', va='top'
                             , fontsize='large', fontfamily='Calibri', linespacing=1.4)
            func_text = '$n (L) = {{{}}} * L^{{{}}}$'.format(np.round(c, 2), np.round(m, 2))
            ax_for_text.text(0.5, 1.02, func_text, transform=ax_for_text.transAxes, ha='center', fontsize='x-large')

        if unified:
            frame_lineframe_main_cut_concat = self.uniframe_lineframe_main_cut_concat
        else:
            frame_lineframe_main_cut_concat = self.df_lineframe_main_cut_concat

        lineframe = frame_lineframe_main_cut_concat
        lineframe = pd.DataFrame(lineframe)
        lineframe['logLen'] = lineframe.length.apply(np.log)
        lineframe['logY'] = lineframe.y.apply(np.log)

        # log(y) = m*log(x) + c fitted     y = c*x^m
        vals = np.polyfit(lineframe['logLen'].values, lineframe['logY'].values, 1)
        if len(vals) == 2:
            m, c = vals[0], vals[1]
        else:
            QgsMessageLog.logMessage(message='Too many values (vals) from np.polyfit, 2 expected.\n'
                                             f'vals: {vals}', tag=__name__, level=Qgis.Critical)
            raise ValueError('Too many values (vals) from np.polyfit, 2 expected.\n'
                             f'vals: {vals}')
        y_fit = np.exp(m * lineframe['logLen'].values + c)  # calculate the fitted values of y
        lineframe['y_fit'] = y_fit
        lineframe.plot(x='length', y='y_fit', color='k', ax=ax, label='Power Law Fit', linestyle='dashed', linewidth=2,
                       alpha=.8)
        create_text(lineframe, ax)

    def plot_lengths(self, unified: bool, save=False, savefolder='', use_sets=False):
        """
        Plots length distributions.

        :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        :param use_sets: Whether to use sets
        :type use_sets: bool
        """

        if unified:
            frame = self.uniframe
        else:
            frame = self.df
        # Get color list
        color_dict = config.get_color_dict(unified)

        for idx, srs in frame.iterrows():
            color_for_plot = color_dict[srs['TargetAreaLines'].name]
            srs['TargetAreaLines'].plot_length_distribution(unified=unified, color_for_plot=color_for_plot)
        if use_sets:
            # TODO: reimplement set length distributions
            raise NotImplementedError('use_sets Not implemented')

        # Figure setup for FULL LDs
        figure_size = (7, 7)
        fig, ax = plt.subplots(figsize=figure_size)
        ax.set_xlim(self.uni_left, self.uni_right)
        ax.set_ylim(self.uni_bottom, self.uni_top)

        # Plot full lds

        for idx, srs in frame.iterrows():
            color_for_plot = color_dict[srs['TargetAreaLines'].name]
            srs['TargetAreaLines']: ta.TargetAreaLines
            srs['TargetAreaLines'].plot_length_distribution_ax(ax=ax, cut=False, color_for_plot=color_for_plot)

        tools.setup_ax_for_ld(ax, self.using_branches)
        # Save figure
        if save:
            if unified:
                savename = Path(savefolder + '/UNIFIED_FULL_LD.png')
            else:
                savename = Path(savefolder + '/ALL_FULL_LD.png')
            plt.savefig(savename, dpi=150, bbox_inches='tight')

        # Figure setup for CUT LDs
        fig, ax = plt.subplots(figsize=figure_size)
        ax.set_xlim(self.uni_left, self.uni_right)
        ax.set_ylim(self.uni_bottom, self.uni_top)

        # Plot cut lds
        length_text = ''
        for idx, srs in frame.iterrows():
            color_for_plot = color_dict[srs['TargetAreaLines'].name]
            srs['TargetAreaLines'].plot_length_distribution_ax(ax=ax, cut=True, color_for_plot=color_for_plot)
            min_length = srs['TargetAreaLines'].lineframe_main_cut.length.min()
            name = srs['group']
            # Text for cut-off lengths
            length_text += f'{name} Cut Off (m) = {str(round(min_length, 2))}'
            if idx == len(frame) - 1:
                # No new line
                pass
            else:
                # Add new line
                length_text += '\n'

        # Plot fit for cut lds
        self.plot_length_fit_cut_ax(ax, unified=unified)

        # Setup ax
        ax.set_xlim(self.uni_left, self.uni_right)
        ax.set_ylim(self.uni_bottom, self.uni_top)

        # Add text with cut-off lengths to plot.
        ax.text(1.3, 0.34, length_text, transform=ax.transAxes, fontsize='large', weight='roman',
                bbox={'boxstyle': 'round', 'facecolor': 'whitesmoke', 'pad': 0.5},
                verticalalignment='top', ha='center', fontfamily='Calibri', linespacing=1.5)
        tools.setup_ax_for_ld(ax, self.using_branches)
        # Save figure
        if save:
            if unified:
                savename = Path(savefolder + '/UNIFIED_CUT_LD_WITH_FIT.png')
            else:
                savename = Path(savefolder + '/ALL_CUT_LD_WITH_FIT.png')
            plt.savefig(savename, dpi=150, bbox_inches='tight')

        if use_sets:
            raise NotImplementedError('Not implemented. Yet.')
            # for curr_set, s in enumerate(self.set_ranges_list):
            #
            #     fig, ax = plt.subplots(figsize=figure_size)  # Figure for full LDs, for each set
            #     #                length_text = 'FULL, SET '+str(idx)+'\nCut Off Lengths (m)\n\n'
            #     for idx, srs in self.uniframe.iterrows():
            #         srs['TargetAreaLines'].plot_length_distribution_ax(ax=ax, use_sets=True, curr_set=curr_set)
            #     #                    min_length = srs['TargetAreaLines'].setframes[curr_set].length.min()
            #     #                    name = srs['name']
            #     #                    length_text = length_text+name+' : '+str(round(min_length, 2))+'\n'
            #     ax.set_xlim(self.uni_left, self.uni_right)
            #     ax.set_ylim(self.uni_bottom, self.uni_top)
            #     tools.setup_ax_for_ld(ax, self)
            #     if save:
            #         savename = Path(savefolder + '/FULL_LD_SET_{}.png'.format(curr_set))
            #         plt.savefig(savename, dpi=150)
            #     fig, ax = plt.subplots(figsize=figure_size)  # Figure for cut LDs, for each set
            #     length_text = 'CUT, SET ' + str(curr_set) + '\nCut Off Lengths (m)\n\n'
            #     for idx, srs in self.uniframe.iterrows():
            #         srs['TargetAreaLines'].plot_length_distribution_ax(ax=ax, cut=True, use_sets=True,
            #                                                            curr_set=curr_set)
            #         min_length = srs['TargetAreaLines'].setframes_cut[curr_set].length.min()
            #         name = srs['name']
            #         length_text = length_text + name + ' : ' + str(round(min_length, 2)) + '\n'
            #
            #     tools.plot_fit_for_uniframe(self, ax=ax, cut=True, use_sets=True, curr_set=curr_set,
            #                                 font_multiplier=1, unified=unified)
            #     ax.set_xlim(self.uni_left, self.uni_right)
            #     ax.set_ylim(self.uni_bottom, self.uni_top)
            #     tools.setup_ax_for_ld(ax, self)
            #     ax.text(0.1, 0.3, length_text, transform=ax.transAxes, fontsize=18, weight='roman',
            #             verticalalignment='top', bbox=props, fontfamily='Times New Roman')
            #     if save:
            #         savename = Path(savefolder + '/CUT_LD_SET_{}.png'.format(curr_set))
            #         plt.savefig(savename, dpi=150)

    def plot_azimuths(self, unified: bool, rose_type: str, save=False, savefolder=''):
        """
        Plots azimuths.

        :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param rose_type: Whether to plot equal-radius or equal-area rose plot e.g. 'equal-radius' or 'equal-area'
        :type rose_type: str
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        """
        branches = self.using_branches

        if unified:
            frame = self.uniframe
        else:
            frame = self.df

        # Individual plots
        for idx, row in frame.iterrows():
            row['TargetAreaLines'].plot_azimuth(rose_type=rose_type, save=save, savefolder=savefolder,
                                                branches=branches)

        # Experimental, one big plot
        plot_count = len(frame)
        if plot_count < 5:
            plot_count = 5
        cols = 4
        rows = plot_count // cols + 1
        width = 26
        height = (width / cols) * (rows * 1.3)
        fig, ax = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
                               , figsize=(width, height))
        fig_w, ax_w = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
                                   , figsize=(width, height))

        for idx, row in frame.iterrows():
            row['TargetAreaLines'].plot_azimuth(rose_type=rose_type, save=False, savefolder=savefolder,
                                                branches=branches
                                                , ax=ax[idx // cols][idx % cols]
                                                , big_plots=True
                                                , ax_w=ax_w[idx // cols][idx % cols])

        top, bottom, left, right, hspace, wspace = 0.90, 0.07, 0.05, 0.95, 0.3, 0.3
        fig.tight_layout()
        fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
        fig_w.tight_layout()
        fig_w.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)

        if save:
            if unified:
                savename = Path(savefolder + '/azimuths_unified_all.png')
                savename_w = Path(savefolder + '/azimuths_unified_WEIGHTED_all.png')
            else:
                savename = Path(savefolder + '/azimuths_all.png')
                savename_w = Path(savefolder + '/azimuths_WEIGHTED_all.png')

            fig.savefig(savename, dpi=150)
            fig_w.savefig(savename_w, dpi=150)

    def plot_azimuths_exp(self, unified: bool, rose_type: str, save=False, savefolder=''):
        """
        Plots azimuths.

        :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param rose_type: Whether to plot equal-radius or equal-area rose plot e.g. 'equal-radius' or 'equal-area'
        :type rose_type: str
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        """
        branches = self.using_branches

        if unified:
            frame = self.uniframe
        else:
            frame = self.df

        # Individual plots
        for idx, row in frame.iterrows():
            row['TargetAreaLines'].plot_azimuth_exp(rose_type=rose_type, save=save, savefolder=savefolder,
                                                    branches=branches)

        # Experimental, one big plot
        plot_count = len(frame)
        if plot_count < 5:
            plot_count = 5
        cols = 4
        rows = plot_count // cols + 1
        width = 26
        height = (width / cols) * (rows * 1.3)
        fig, ax = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
                               , figsize=(width, height))
        fig_w, ax_w = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
                                   , figsize=(width, height))

        for idx, row in frame.iterrows():
            row['TargetAreaLines'].plot_azimuth_exp(rose_type=rose_type, save=False, savefolder=savefolder,
                                                    branches=branches
                                                    , ax=ax[idx // cols][idx % cols]
                                                    , big_plots=True
                                                    , ax_w=ax_w[idx // cols][idx % cols])

        top, bottom, left, right, hspace, wspace = 0.90, 0.07, 0.05, 0.95, 0.3, 0.3
        fig.tight_layout()
        fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
        fig_w.tight_layout()
        fig_w.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)

        if save:
            if unified:
                savename = Path(savefolder + '/azimuths_unified_all.png')
                savename_w = Path(savefolder + '/azimuths_unified_WEIGHTED_all.png')
            else:
                savename = Path(savefolder + '/azimuths_all.png')
                savename_w = Path(savefolder + '/azimuths_WEIGHTED_all.png')

            fig.savefig(savename, dpi=150)
            fig_w.savefig(savename_w, dpi=150)

    def plot_azimuths_weighted(self, unified: bool, save=False, savefolder=''):
        branches = self.using_branches

        if unified:
            frame = self.uniframe
        else:
            frame = self.df

        # Individual plots
        for idx, row in frame.iterrows():
            name = row.TargetAreaLines.name
            ph = 'group' if unified else 'area'
            fold = 'branches' if branches else 'traces'
            row['TargetAreaLines'].plot_azimuth_weighted(rose_type='equal-radius', set_visualization=False)
            if save:
                if unified:
                    savename = Path(savefolder + f'/equal_radius/{fold}/{name}_{ph}_weighted_azimuths.png')
                else:
                    savename = Path(savefolder + f'/equal_radius/{fold}/{name}_{ph}_weighted_azimuths.png')

                plt.savefig(savename, dpi=150, bbox_inches='tight')

            row['TargetAreaLines'].plot_azimuth_weighted(rose_type='equal-area', set_visualization=False)
            if save:
                if unified:
                    savename = Path(savefolder + f'/equal_area/{fold}/{name}_{ph}_weighted_azimuths.png')
                else:
                    savename = Path(savefolder + f'/equal_area/{fold}/{name}_{ph}_weighted_azimuths.png')

                plt.savefig(savename, dpi=150, bbox_inches='tight')

    # noinspection PyArgumentList
    def determine_crosscut_abutting_relationships(self, unified: bool):
        """
        Determines cross-cutting and abutting relationships between all inputted sets by using spatial intersects
        between node and trace data. Sets result as a class parameter self.relations_df that is used for plotting.

        :param unified: Calculate for unified datasets or individual target areas
        :type unified: bool
        :raise AssertionError: When attempting to determine cross-cutting and abutting relationships from branch data
            or if self.using_branches is True even though you are using trace data.
        :raise ValueError: When there's only one set defined.
            You cannot determine cross-cutting and abutting relationships from only one set.
        """
        # Determines xy relations and dynamically creates a dataframe as an aid for plotting the relations
        # TODO: No within set relations.....yet... Problem?
        if self.using_branches:
            raise AssertionError('Cross-cutting and abutting relationships cannot be determined from BRANCH data.')

        # name: Contains target area name, Sets: (1, 2),
        # x: x nodes between the sets, y: 1 abuts to 2 y node count, y-reverse: 2 abuts to 1 y node count
        relations_df = pd.DataFrame(columns=['name', 'sets', 'x', 'y', 'y-reverse', 'error-count'])

        if unified:
            frame = self.uniframe
        else:
            frame = self.df

        plotting_set_counts = {}
        for _, row in frame.iterrows():
            name = row.TargetAreaNodes.name
            nodeframe = row.TargetAreaNodes.nodeframe
            traceframe = row.TargetAreaLines.lineframe_main
            # Initializing
            traceframe['startpoint'] = traceframe.geometry.apply(tools.line_start_point)
            traceframe['endpoint'] = traceframe.geometry.apply(tools.line_end_point)
            traceframe = traceframe.reset_index(drop=True)
            nodeframe = nodeframe.loc[(nodeframe.c == 'X') | (nodeframe.c == 'Y')]
            xypointsframe = nodeframe.reset_index(drop=True)

            sets = self.set_df.Set.tolist()

            if len(sets) < 2:
                raise ValueError('Only one set defined. Cannot determine cross-cutting and abutting relationships')
            # COLOR CYCLE FOR BARS

            # START OF COMPARISONS
            for idx, s in enumerate(sets):
                # If final set: Skip the final set, comparison already done.
                if idx == len(sets) - 1:
                    break
                compare_sets = sets[idx + 1:]

                for jdx, c_s in enumerate(compare_sets):

                    # QgsMessageLog.logMessage(message=f'traceframe: {traceframe}\n\n\nsets: {sets}\ns: {s}\nc_s: {c_s}'
                    #                                  f'\ntraceframe sets {traceframe.set.unique().tolist()}')

                    traceframe_two_sets = traceframe.loc[(traceframe['set'] == s) | (traceframe['set'] == c_s)]
                    # TODO: More stats for cross-cutting and abutting relationships?

                    intersecting_nodes_frame = tools.get_nodes_intersecting_sets(xypointsframe, traceframe_two_sets)

                    intersectframe = tools.get_intersect_frame(intersecting_nodes_frame, traceframe_two_sets, (s, c_s))

                    if len(intersectframe.loc[intersectframe.error == True]) > 0:
                        QgsMessageLog.logMessage(message='There were errors in creating intersectframe.\n'
                                                         f'Error count: {len(intersectframe.loc[intersectframe.error == True])}'
                                                 , tag=__name__, level=Qgis.Warning)

                    intersect_series = intersectframe.groupby(['nodeclass', 'sets']).size()

                    x_count = 0
                    y_count = 0
                    y_reverse_count = 0

                    for item in [s for s in intersect_series.iteritems()]:
                        value = item[1]
                        if item[0][0] == 'X':
                            x_count = value
                        elif item[0][0] == 'Y':
                            if item[0][1] == (s, c_s):  # it's set s abutting in set c_s
                                y_count = value
                            elif item[0][1] == (c_s, s):  # it's set c_s abutting in set s
                                y_reverse_count = value
                            else:
                                raise ValueError(
                                    f'item[0][1] doesnt equal {(s, c_s)} nor {(c_s, s)}\nitem[0][1]: {item[0][1]}')
                        else:
                            raise ValueError(f'item[0][0] doesnt match "X" or "Y"\nitem[0][0]: {item[0][0]}')

                    addition = {'name': name, 'sets': (s, c_s)
                        , 'x': x_count, 'y': y_count, 'y-reverse': y_reverse_count
                        , 'error-count': len(intersectframe.loc[intersectframe.error == True])}

                    relations_df = relations_df.append(addition, ignore_index=True)
        if unified:
            self.unified_relations_df = relations_df
        else:
            self.relations_df = relations_df

    def plot_crosscut_abutting_relationships(self, unified: bool, save=False, savefolder=''):
        """
        Plots cross-cutting and abutting relationships for individual target areas or for grouped data.

        :param unified: Calculate for unified datasets or individual target areas
        :type unified: bool
        :param save: Save plots or not
        :type save: bool
        :param savefolder: Folder to save plots to
        :type savefolder: str
        :raise TypeError: When attempting to determine cross-cutting and abutting relationships from branch data
            or if self.using_branches is True even though you are using trace data.
        """
        if unified:
            frame = self.uniframe
            rel_frame = self.unified_relations_df
        else:
            frame = self.df
            rel_frame = self.relations_df

        if self.using_branches:
            raise TypeError('Cross-cutting and abutting relationships cannot be determined from BRANCH data.')

        # SUBPLOTS, FIGURE SETUP
        cols = len(list(itertools.combinations(self.set_df["Set"].tolist(), r=2)))
        # QgsMessageLog.logMessage(message=f"cols: {cols}", tag=__name__, level=Qgis.Warning)
        if cols == 2:
            cols = 1
        width = 12 / 3 * cols
        height = (width / cols) * 0.75
        names = set(rel_frame.name.tolist())
        with plt.style.context('default'):
            for name in names:
                rel_frame_with_name = rel_frame.loc[rel_frame.name == name]
                frame_with_name = frame.loc[frame.name == name]
                if len(frame_with_name) != 1:
                    raise Exception(f'Multiple frames with name == name in frame. Unified: {unified}')
                set_names = self.set_df.Set.tolist()
                set_counts = []
                lineframe = frame_with_name.iloc[0].TargetAreaLines.lineframe_main

                for set_name in set_names:
                    set_counts.append(len(lineframe.loc[lineframe.set == set_name]))

                fig, axes = plt.subplots(ncols=cols, nrows=1, figsize=(width, height))
                if not isinstance(axes, np.ndarray):
                    axes = [axes]

                prop_title = dict(boxstyle='square', facecolor='linen', alpha=1, linewidth=2)

                fig.suptitle(f'   {name}   ', x=0.19, y=1.0,
                             fontsize=20, fontweight='bold', fontfamily='Calibri'
                             , va='center', bbox=prop_title)

                for ax, idx_row in zip(axes, rel_frame_with_name.iterrows()):
                    ax: matplotlib.axes._subplots.AxesSubplot
                    row = idx_row[1]
                    # TODO: More colors? change brightness or some other parameter?
                    bars = ax.bar(x=[0.3, 0.55, 0.65]
                                  , height=[row['x'], row['y'], row['y-reverse']]
                                  , width=0.1
                                  , color=['darkgrey', 'darkolivegreen', 'darkseagreen']
                                  , linewidth=1
                                  , edgecolor='black'
                                  , alpha=0.95
                                  , zorder=10)

                    ax.legend(bars, (f'Sets {row.sets[0]} and {row.sets[1]} cross-cut'
                                     , f'Set {row.sets[0]} abuts to set {row.sets[1]}'
                                     , f'Set {row.sets[1]} abuts to set {row.sets[0]}')
                              , framealpha=1
                              , loc='upper center'
                              , edgecolor='black'
                              , prop={'family': 'Calibri'})

                    ax.set_ylim(0, 1.6 * max([row['x'], row['y'], row['y-reverse']]))

                    ax.grid(zorder=-10, color='black', alpha=0.5)

                    xticks = [0.3, 0.6]
                    xticklabels = ['X', 'Y']
                    ax.set_xticks(xticks)
                    ax.set_xticklabels(xticklabels)

                    xticklabels = ax.get_xticklabels()

                    for xtick in xticklabels:
                        xtick.set_fontweight('bold')
                        xtick.set_fontsize(12)

                    ax.set_xlabel('Node type', fontweight='bold', fontsize=13, fontstyle='italic', fontfamily='Calibri')
                    ax.set_ylabel('Node count', fontweight='bold', fontsize=13, fontstyle='italic',
                                  fontfamily='Calibri')

                    plt.subplots_adjust(wspace=0.3)

                    if ax == axes[-1]:
                        text = ''
                        prop = dict(boxstyle='square', facecolor='linen', alpha=1, pad=0.45)
                        for set_label, set_len in zip(set_names, set_counts):
                            text += f'Set {set_label} trace count: {set_len}'
                            if not set_label == set_names[-1]:
                                text += '\n'
                        ax.text(1.1, 0.5, text
                                , rotation=90
                                , transform=ax.transAxes
                                , va='center'
                                , bbox=prop
                                , fontfamily='Calibri')
                if save:
                    savename = Path(savefolder + f'/{name}_crosscutting_abutting_relationships.png')
                    plt.savefig(savename, dpi=200, bbox_inches='tight')

    def plot_xyi_ternary(self, unified: bool, save=False, savefolder=''):
        """
        Plots XYI-ternary plots for target areas or grouped areas.

        :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        """
        if unified:
            frame = self.uniframe
        else:
            frame = self.df
        color_dict = config.get_color_dict(unified)
        fig, ax = plt.subplots(figsize=(6.5, 5.1))
        scale = 100

        fig, tax = ternary.figure(ax=ax, scale=scale)
        tools.initialize_ternary_points(ax, tax)
        for idx, row in frame.iterrows():
            color_for_plot = color_dict[row['TargetAreaNodes'].name]
            row['TargetAreaNodes'].plot_xyi_point(tax=tax, color_for_plot=color_for_plot)
        tools.tern_plot_the_fing_lines(tax)
        tax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), title='XYI-Nodes', title_fontsize='xx-large',
                   prop={'family': 'Calibri', 'weight': 'heavy', 'size': 'x-large'}, edgecolor='black', ncol=2,
                   columnspacing=0.7, shadow=True)
        if save:
            if unified:
                savename = Path(savefolder + '/unified_xyi_points.png')
            else:
                savename = Path(savefolder + '/all_xyi_points.png')
            plt.savefig(savename, dpi=150, bbox_inches='tight')

        # MAKE INDIVIDUAL XYI PLOTS
        for idx, row in frame.iterrows():
            color_for_plot = color_dict[row['TargetAreaNodes'].name]
            row['TargetAreaNodes'].plot_xyi_plot(unified=unified, color_for_plot=color_for_plot, save=save,
                                                 savefolder=savefolder)

    def plot_branch_ternary(self, unified: bool, save=False, savefolder=''):
        """
        Plots Branch classification-ternary plots for target areas or grouped data.

        :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str

        """
        if not self.using_branches:
            raise Exception('Branch classifications cannot be determined from traces.')
        fig, ax = plt.subplots(figsize=(6.5, 5.1))
        scale = 100
        fig, tax = ternary.figure(ax=ax, scale=scale)
        tools.initialize_ternary_branches_points(ax, tax)
        if unified:
            frame = self.uniframe
        else:
            frame = self.df
        color_dict = config.get_color_dict(unified)
        for _, row in frame.iterrows():
            color_for_plot = color_dict[row['TargetAreaLines'].name]
            row['TargetAreaLines'].plot_branch_ternary_point(tax=tax, color_for_plot=color_for_plot)
        tools.tern_plot_branch_lines(tax)
        tax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), title='Branch Classes', title_fontsize='xx-large',
                   prop={'family': 'Calibri', 'weight': 'heavy', 'size': 'x-large'}, edgecolor='black', ncol=2,
                   columnspacing=0.7, shadow=True)
        # plt.subplots_adjust(top=0.8)
        if save:
            if unified:
                savename = Path(savefolder + '/unified_branch_points.png')
            else:
                savename = Path(savefolder + '/all_branch_points.png')
            plt.savefig(savename, dpi=150, bbox_inches='tight')

        for _, row in frame.iterrows():
            color_for_plot = color_dict[row['TargetAreaLines'].name]
            row['TargetAreaLines'].plot_branch_ternary_plot(unified=unified, color_for_plot=color_for_plot, save=True,
                                                            savefolder=savefolder)

    def gather_topology_parameters(self, unified: bool):
        """
        Gathers topological parameters of both traces and branches

        :param unified: Use unified datasets or individual target areas
        :type unified: bool
        :return:
        :rtype:
        """
        branches = self.using_branches
        if unified:
            self.uniframe['topology'] = None
            frame = self.uniframe
        else:
            self.df['topology'] = None
            frame = self.df
        topology_appends = []
        for idx, row in frame.iterrows():
            name = row.TargetAreaLines.name
            ld = row.TargetAreaLines
            nd = row.TargetAreaNodes
            params_ld = ld.topology_parameters_2d_branches(branches=branches)
            params_nd = nd.topology_parameters_2d_nodes()
            if branches:
                fracture_intensity, aerial_frequency, characteristic_length \
                    , dimensionless_intensity, number_of_lines, connection_dict = params_ld
            else:
                fracture_intensity, aerial_frequency, characteristic_length \
                    , dimensionless_intensity, number_of_lines = params_ld

            node_dict = params_nd

            connections_per_line = 2 * (node_dict['Y'] + node_dict['X']) / number_of_lines
            connections_per_branch = (3 * node_dict['Y'] + 4 * node_dict['X']) / number_of_lines
            if branches:
                topology_dict = {'name': name,
                                 'Number of Branches': number_of_lines,
                                 'C - C': connection_dict['C - C'],
                                 'C - I': connection_dict['C - I'],
                                 'I - I': connection_dict['I - I'],
                                 'X': node_dict['X'],
                                 'Y': node_dict['Y'],
                                 'I': node_dict['I'],
                                 'Mean Length': characteristic_length,
                                 'Connections per Branch': connections_per_branch,
                                 'Areal Frequency B20': aerial_frequency,
                                 'Fracture Intensity B21': fracture_intensity,
                                 'Dimensionless Intensity B22': dimensionless_intensity}
            else:
                topology_dict = {'name': name,
                                 'Number of Traces': number_of_lines,
                                 'X': node_dict['X'],
                                 'Y': node_dict['Y'],
                                 'I': node_dict['I'],
                                 'Mean Length': characteristic_length,
                                 'Connections per Trace': connections_per_line,
                                 'Areal Frequency P20': aerial_frequency,
                                 'Fracture Intensity P21': fracture_intensity,
                                 'Dimensionless Intensity P22': dimensionless_intensity}
            topology_appends.append([idx, topology_dict])
        for topology in topology_appends:
            idx = topology[0]
            topo = topology[1]
            topoframe = pd.DataFrame()
            topoframe = topoframe.append(topo, ignore_index=True)
            frame.topology[idx] = topoframe
        if unified:
            self.uniframe_topology_concat = pd.concat(frame.topology.tolist(), ignore_index=True)
        else:
            self.df_topology_concat = pd.concat(frame.topology.tolist(), ignore_index=True)

    def plot_topology(self, unified: bool, save=False, savefolder=''):
        """
        Plot topological parameters

        :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        """
        branches = self.using_branches
        log_scale_columns = ['Mean Length', 'Areal Frequency B20',
                             'Fracture Intensity B21', 'Fracture Intensity P21', 'Areal Frequency P20']
        prop = config.prop
        units_for_columns = config.units_for_columns
        color_dict = config.get_color_dict(unified)
        if unified:
            topology_concat = self.uniframe_topology_concat
        else:
            topology_concat = self.df_topology_concat
        # Add color column to topology_concat DataFrame
        topology_concat['color'] = topology_concat.name.apply(lambda n: color_dict[n])

        if branches:
            columns_to_plot = ['Mean Length', 'Connections per Branch',
                               'Areal Frequency B20', 'Fracture Intensity B21',
                               'Dimensionless Intensity B22']
        else:
            columns_to_plot = ['Mean Length', 'Connections per Trace',
                               'Areal Frequency P20', 'Fracture Intensity P21',
                               'Dimensionless Intensity P22']

        for column in columns_to_plot:
            # Figure size setup
            # TODO: width higher, MAYBE lower bar_width
            if unified:
                width = 6 + 1 * len(self.group_names_cutoffs_df) / 6
                bar_width = 0.6 * len(self.group_names_cutoffs_df) / 6

            else:
                width = 6 + 1 * len(self.table_df) / 6
                bar_width = 0.6 * len(self.table_df) / 6

            fig, ax = plt.subplots(figsize=(width, 5.5))
            topology_concat.name = topology_concat.name.astype('category')
            # Trying to have sensible widths for bars:
            topology_concat.plot.bar(x='name', y=column, color=topology_concat.color.values,
                                     zorder=5, alpha=0.9, width=bar_width, ax=ax)
            # PLOT STYLING
            ax.set_xlabel('')
            ax.set_ylabel(column + ' ' + f'({units_for_columns[column]})', fontsize='xx-large', fontfamily='Calibri'
                          , style='italic')
            ax.set_title(x=0.5, y=1.09, label=column, fontsize='xx-large',
                         bbox=prop, transform=ax.transAxes, zorder=-10)
            legend = ax.legend()
            legend.remove()
            if column in log_scale_columns:
                ax.set_yscale('log')
            fig.subplots_adjust(top=0.85, bottom=0.25, left=0.2)
            locs, labels = plt.xticks()
            labels = ['\n'.join(wrap(l.get_text(), 6)) for l in labels]
            plt.yticks(fontsize='xx-large', color='black')
            plt.xticks(locs, labels, fontsize='xx-large', color='black')
            # MOD xTICKS
            # CHANGE LEGEND HANDLES WITHOUT CHANGING PLOT
            # for t in xticks:
            #     lh._sizes = [30]

            # VALUES ABOVE BARS WITH TEXTS
            rects = ax.patches
            for value, rect in zip(topology_concat[column], rects):
                height = rect.get_height()
                if value > 0.01:
                    value = round(value, 2)
                else:
                    value = '{0:.2e}'.format(value)
                if column in log_scale_columns:
                    height = height + height / 10
                else:
                    max_height = max([r.get_height() for r in rects])
                    height = height + max_height / 100
                ax.text(rect.get_x() + rect.get_width() / 2, height, value,
                        ha='center', va='bottom', zorder=15, fontsize='x-large')

            if save:
                if unified:
                    savename = Path(savefolder + '/{}_unified.png'.format(str(column)))
                else:
                    savename = Path(savefolder + '/{}_all.png'.format(str(column)))
                plt.savefig(savename, dpi=150)

    def plot_hexbin_plot(self, unified: bool, save=False, savefolder=''):
        """
        Plot a hexbinplot to estimate sample size differences.

       :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        :return:
        :rtype:
        """
        branches = self.using_branches
        if unified:
            lf = self.uniframe_lineframe_main_concat
        else:
            lf = self.df_lineframe_main_concat
        # Create Fig and gridspec
        fig = plt.figure(figsize=(10, 10), dpi=80)
        grid = plt.GridSpec(4, 5, hspace=0.5, wspace=0.2)
        # Define the axes
        ax_main = fig.add_subplot(grid[:-1, :-1])
        ax_bottom = fig.add_subplot(grid[-1, 0:-1], xticklabels=[], yticklabels=[])
        ax_right = fig.add_subplot(grid[:-1, -1], xticklabels=[], yticklabels=[])
        # Hexbinplot on main ax
        hb = ax_main.hexbin(np.log(lf.length.values), np.log(lf.y.values), gridsize=75, bins='log', cmap='inferno',
                            mincnt=1)
        # histogram, bottom
        ax_bottom.hist(np.log(lf.length.values), 40, histtype='stepfilled', orientation='vertical', color='deeppink')
        ax_bottom.invert_yaxis()
        # Make all tick labels invisible
        for label in ax_main.get_xmajorticklabels():
            label.set_visible(False)
        for label in ax_main.get_ymajorticklabels():
            label.set_visible(False)
        # Labels for all axes
        ax_bottom.set_ylabel('Line Count\nHistogram', visible=True, fontsize=25, style='italic')
        if branches:
            ax_main.set_xlabel('Branch Length', labelpad=10, fontsize=24, style='italic')
        else:
            ax_main.set_xlabel('Trace Length', labelpad=10, fontsize=24, style='italic')

        ax_main.set_ylabel('Complementary Cumulative\nNumber', labelpad=10, fontsize=24, style='italic')
        # Title
        if branches:
            fig.suptitle('Comparison of Group datasets\nBranches', fontsize=26)
        else:
            fig.suptitle('Comparison of Group datasets\nTraces', fontsize=26)
        # Colorbar
        cb = fig.colorbar(hb, cax=ax_right)
        cb.set_label('Line Count Colorbar', fontsize=26)
        # Saving the figure
        if save:
            if unified:
                if branches:
                    savename = Path(savefolder + '/unified_hexbinplot_branches_with_histo.png')
                else:
                    savename = Path(savefolder + '/unified_hexbinplot_traces_with_histo.png')
                plt.savefig(savename, dpi=200)
            else:
                if branches:
                    savename = Path(savefolder + '/all_hexbinplot_branches_with_histo.png')
                else:
                    savename = Path(savefolder + '/all_hexbinplot_traces_with_histo.png')
            plt.savefig(savename, dpi=200)

    def calc_anisotropy(self, unified: bool):
        if not self.using_branches:
            raise Exception('Anisotropy cannot be determined from traces.')
        if unified:
            frame = self.uniframe
        else:
            frame = self.df
        for idx, row in frame.iterrows():
            row.TargetAreaLines.calc_anisotropy()

    def plot_anisotropy(self, unified: bool, save=False, savefolder=''):
        """
        Plot anisotropy of connectivity

        :param unified: Plot unified datasets or individual target areas
        :type unified: bool
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        """
        if not self.using_branches:
            raise Exception('Anisotropy cannot be determined from traces.')

        if unified:
            frame = self.uniframe
        else:
            frame = self.df

        for idx, row in frame.iterrows():
            row.TargetAreaLines.plot_anisotropy_styled()
            style = config.styled_text_dict
            prop = config.styled_prop
            plt.title(row.TargetAreaLines.name, loc='center', fontdict=style, fontsize=25, bbox=prop)
            if save:
                if unified:
                    savename = Path(savefolder + '/{}_anisotropy_unified.png'.format(row.TargetAreaLines.name))
                else:
                    savename = Path(savefolder + '/{}_anisotropy.png'.format(row.TargetAreaLines.name))

                plt.savefig(savename, dpi=200, bbox_inches="tight")
