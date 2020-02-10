# Python Windows co-operation imports
import logging
from pathlib import Path

import geopandas as gpd
import matplotlib.patches as patches
import matplotlib.patheffects as path_effects
# Math and analysis imports
# Plotting imports
# DataFrame analysis imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import ternary
from scipy.interpolate import make_interp_spline

# Own code imports
from . import tools
from ... import config


# Classes

class TargetAreaLines:
    # TODO: Add using_branches to ld as well?
    def __init__(self, lineframe, areaframe, name, group, using_branches: bool, cut_off=1.0):
        """
        Init of TargetAreaLines
        :param lineframe: GeoDataFrame containing line data
        :type lineframe: gpd.GeoDataFrame
        :param areaframe: GeoDataFrame containing area data
        :type areaframe: gpd.GeoDataFrame
        :param name: Name of the target area (user input)
        :type name: str
        :param group: Group of the target area
        :type group: str
        :param using_branches: Branches or traces
        :type using_branches: bool
        :param cut_off: Cut-off value
        :type cut_off: float
        """

        self.lineframe = lineframe
        self.areaframe = areaframe
        self.group = group
        self.name = name
        self.cut_off = cut_off

        # Get area using geopandas
        if isinstance(lineframe, gpd.GeoDataFrame):
            self.area = sum([polygon.area for polygon in self.areaframe.geometry])
        else:
            try:
                self.area = self.areaframe['Shape_Area'].sum()
            except KeyError:
                self.area = self.areaframe['SHAPE_Area'].sum()

        self.using_branches = using_branches

        # Get line length using geopandas
        if isinstance(lineframe, gpd.GeoDataFrame):
            self.lineframe['length'] = lineframe.geometry.length
        else:
            try:
                self.lineframe['length'] = lineframe['Shape_Leng'].astype(str).astype(float)
            except KeyError:
                self.lineframe['length'] = lineframe['SHAPE_Leng'].astype(str).astype(float)

        # Assign None to later initialized attributes
        # TODO: TEST PROPERLY
        # TODO: lineframe_main initialized as none.... here..... is it a problem?
        self.lineframe_main = None
        self.cut_off_length = None
        self.two_halves = None
        self.left, self.right, self.bottom, self.top = None, None, None, None
        self.lineframe_main_cut = None
        self.set_list = None
        self.setframes = None
        self.setframes_cut = None
        self.anisotropy = None
        self.two_halves_non_weighted = None
        self.two_halves_weighted = None
        self.bin_locs = None
        self.number_of_azimuths = None
        self.bin_width = None
        self.set_df = None

    def calc_attributes(self):
        """
        Calculates important attributes of target area
        :return:
        :rtype:
        """
        self.lineframe_main = self.lineframe.sort_values(by=['length'], ascending=False)
        self.lineframe_main = tools.calc_y_distribution(self.lineframe_main, self.area)

        self.lineframe_main['azimu'] = self.lineframe_main.geometry.apply(tools.calc_azimu)
        # TODO: TEST AND UNDERSTAND WHY THERE ARE nan in AZIMU CALC
        self.lineframe_main = self.lineframe_main.dropna(subset=['azimu'])
        self.lineframe_main['halved'] = self.lineframe_main.azimu.apply(tools.azimu_half)

        self.cut_off_length = tools.calc_cut_off_length(self.lineframe_main, self.cut_off)

        # Allows plotting of azimuth
        self.two_halves_non_weighted = tools.azimuth_plot_attributes(self.lineframe_main, weights=False)
        self.two_halves_weighted = tools.azimuth_plot_attributes(self.lineframe_main, weights=True)
        # Experimental azimuth
        self.bin_width, self.bin_locs, self.number_of_azimuths = tools.azimuth_plot_attributes_experimental(
            lineframe=self.lineframe_main, weights=False)
        # Length distribution plot limits
        self.left, self.right = tools.calc_xlims(self.lineframe_main)
        self.top, self.bottom = tools.calc_ylims(self.lineframe_main)

        self.lineframe_main_cut = self.lineframe_main.loc[self.lineframe_main['length'] >= self.cut_off_length]
        # Reinforce numeric columns

        logger = logging.getLogger('logging_tool')
        # logger.info('self.lineframe_main\n\n{}'.format(self.lineframe_main))
        # logger.info('self.lineframe_main dtypes\n\n{}'.format(self.lineframe_main.dtypes))
        # logger.info('self.lineframe_main_cut\n\n{}'.format(self.lineframe_main_cut))
        # logger.info('self.lineframe_main_cut dtypes\n\n{}'.format(self.lineframe_main_cut.dtypes))

    # list_of_tuples, tuples must be between 0-180
    def define_sets(self, set_df):
        """
        Categorizes both non-cut and cut DataFrames with set limits
        :param set_df: DataFrame with set limits and set names
        :type set_df: DataFrame
        """
        self.lineframe_main['set'] = self.lineframe_main.apply(lambda x: tools.define_set(x['halved'], set_df)
                                                               , axis=1)
        self.lineframe_main_cut['set'] = self.lineframe_main_cut.apply(
            lambda x: tools.define_set(x['halved'], set_df)
            , axis=1)
        set_list = set_df.Set.tolist()
        self.set_df = set_df
        self.set_list = set_list

    def calc_curviness(self):
        self.lineframe_main['curviness'] = self.lineframe_main.geometry.apply(tools.curviness)

    def plot_length_distribution(self, save=False, savefolder=None):
        """
        Plots a length distribution to its own figure.
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        :return:
        :rtype:
        """
        fig, ax = plt.subplots()
        self.plot_length_distribution_ax(ax)
        tools.setup_ax_for_ld(ax, self, font_multiplier=0.5)
        if save:
            name = self.name
            savename = Path(savefolder + '/{}_indiv_full.png'.format(name))
            plt.savefig(savename, dpi=150)

    def plot_length_distribution_ax(self, ax, cut=False, use_sets=False, curr_set=-1):
        """
        Plots a length distribution to a given figure
        :param ax: Ax to plot to
        :type ax: matplotlib.axes.Axes
        :param cut: Whether to cut length distribution using cut-off
        :type cut: bool
        :param use_sets: Plot length distribution for each set
        :type use_sets: bool
        :param curr_set:
        :type curr_set: int
        :return:
        :rtype:
        """
        logger = logging.getLogger('logging_tool')
        ld = self
        if cut and use_sets:
            setframes_cut = self.setframes_cut
            for setframe_cut in setframes_cut:
                s = setframe_cut.set.iloc[0]
                if s == curr_set:
                    setframe_cut = pd.DataFrame(setframe_cut)
                    name = self.name
                    setframe_cut.plot.scatter(x='length', y='y', logx=True, logy=True,
                                              label=name + '_cut_set_' + str(s), ax=ax,
                                              color='black')

        elif cut:
            logger.info('elif cut')
            logger.info('self.lineframe_main_cut:\n\n {}'.format(self.lineframe_main_cut))

            lineframe_cut = self.lineframe_main_cut
            lineframe_cut = pd.DataFrame(lineframe_cut)
            logger.info('lineframe_cut: {}'.format(lineframe_cut))
            logger.info(f'nans: {lineframe_cut.isnull().sum().sum()}')
            lineframe_cut.plot.scatter(x='length', y='y', logx=True, logy=True, label=self.name + '_cut', ax=ax,
                                       color='black')

        elif use_sets:
            raise Exception('not implemented')
            # setframes = self.setframes
            # for setframe in setframes:
            #     s = setframe.set.iloc[0]
            #     if s == curr_set:
            #         setframe = pd.DataFrame(setframe)
            #
            #         setframe.plot.scatter(x='length', y='y', logx=True, logy=True, label=self.name + '_full_set_' + str(s),
            #                               ax=ax, color='black')

        else:
            # with open(r'C:\QGIS_Files\log\log.txt', mode='a') as logfile:
            #     logfile.write('lineframe_main print before gdf to df\n{}'.format(self.lineframe_main))
            #     logfile.write('----------------------------')

            lineframe_main = self.lineframe_main
            lineframe_main = pd.DataFrame(lineframe_main)
            # with open(r'C:\QGIS_Files\log\log.txt', mode='a') as logfile:
            #     logfile.write('lineframe_main print after\n{}'.format(lineframe_main))
            #     logfile.write('----------------------------')
            lineframe_main.plot.scatter(x='length', y='y', s=50, logx=True, logy=True, label=self.name + '_full', ax=ax,
                                        color='black')

    def plot_curviness(self, cut_data=False):
        fig = plt.figure()
        ax = plt.gca()
        if ~cut_data:
            lineframe = self.lineframe_main
        else:
            lineframe = self.lineframe_main_cut
        name = self.name
        lineframe['set'] = lineframe.set.astype('category')
        sns.boxplot(data=lineframe, x='curviness', y='set', notch=True, ax=ax)
        ax.set_title(name, fontsize=14, fontweight='heavy', fontfamily='Times New Roman')
        ax.set_ylabel('Set (°)', fontfamily='Times New Roman', style='italic')
        ax.set_xlabel('Curvature (°)', fontfamily='Times New Roman', style='italic')
        ax.grid(True, color='k', linewidth=0.3)
        plt.savefig(Path('plots/curviness/{}.png'.format(name)), dpi=100)

    def plot_curviness_violins(self, cut_data=False):
        fig = plt.figure()
        ax = plt.gca()
        if ~cut_data:
            lineframe = self.lineframe_main
        else:
            lineframe = self.lineframe_main_cut
        name = self.name
        lineframe['set'] = lineframe.set.astype('category')
        sns.violinplot(data=lineframe, x='curviness', y='set', ax=ax)
        ax.set_title(name, fontsize=14, fontweight='heavy', fontfamily='Times New Roman')
        ax.set_ylabel('Set', fontfamily='Times New Roman', style='italic')
        ax.set_xlabel('Curvature (°)', fontfamily='Times New Roman', style='italic')
        ax.grid(True, color='k', linewidth=0.3)
        ax.set_xlim(left=0)
        plt.savefig(Path('plots/curviness/{}_violin.png'.format(name)), dpi=100)

    def create_setframes(self):
        sets = self.lineframe_main.set.unique()
        sets.sort()

        setframes = []
        setframes_cut = []
        for s in sets:
            setframe = self.lineframe_main.loc[self.lineframe_main.set == s]
            setframe_cut = self.lineframe_main_cut.loc[self.lineframe_main_cut.set == s]
            setframe = tools.calc_y_distribution(setframe, self.area)
            setframe_cut = tools.calc_y_distribution(setframe_cut, self.area)
            setframes.append(setframe)
            setframes_cut.append(setframe_cut)
        self.setframes = setframes
        self.setframes_cut = setframes_cut

    def plot_azimuth(self, rose_type, save=False, savefolder=None, branches=False, big_plots=False
                     , ax=None, ax_w=None):
        """
        Plot azimuth to either ax or to its own figure,
        in which case both non-weighted and weighted versions area made.
        :param rose_type: Whether to plot equal-radius or equal-area rose plot e.g. 'equal-radius' or 'equal-area'
        :type rose_type: str
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        :param branches: Branches or traces
        :type branches: bool
        :param big_plots: Plotting to a big plot or to an individual one
        :type big_plots: bool
        :param ax: Ax to plot to
        :type ax: matplotlib.projections.polar.PolarAxes
        :param ax_w: Weighted azimuth ax to plot to
        :type ax_w: matplotlib.projections.polar.PolarAxes
        """
        if big_plots:

            self.plot_azimuth_ax(ax=ax, name=self.name, weights=False, rose_type=rose_type, font_multiplier=0.5)
            self.plot_azimuth_ax(ax=ax_w, name=self.name, weights=True, rose_type=rose_type, font_multiplier=0.5)

        else:
            # Non-weighted
            fig, ax = plt.subplots(subplot_kw=dict(polar=True), constrained_layout=True, figsize=(6.5, 5.1))
            self.plot_azimuth_ax(ax=ax, name=self.name, weights=False, rose_type=rose_type, font_multiplier=1)

            if save:
                if branches:
                    savename = Path(savefolder + '/{}_azimuth_branches.png'.format(self.name))
                else:
                    savename = Path(savefolder + '/{}_azimuth_traces.png'.format(self.name))
                plt.savefig(savename, dpi=150)
            # Weighted
            fig, ax_w = plt.subplots(subplot_kw=dict(polar=True), constrained_layout=True, figsize=(6.5, 5.1))
            self.plot_azimuth_ax(ax=ax_w, name=self.name, weights=True, rose_type=rose_type, font_multiplier=1)
            if save:
                if branches:
                    savename = Path(savefolder + '/{}_azimuth_branches_WEIGHTED.png'.format(self.name))
                else:
                    savename = Path(savefolder + '/{}_azimuth_traces_WEIGHTED.png'.format(self.name))
                plt.savefig(savename, dpi=150)

    def plot_azimuth_ax(self, ax, name, weights, rose_type, font_multiplier=1.0):
        """
        Plot azimuth to ax. Text size can be changed with a multiplier.
        :param ax: Polar axis to plot to.
        :type ax: matplotlib.projections.polar.PolarAxes
        :param name: Name used
        :type name: str
        :param weights: Whether to weighted or not
        :type weights: bool
        :param rose_type: Whether to plot equal-radius or equal-area rose plot e.g. 'equal-radius' or 'equal-area'
        :type rose_type: str
        :param font_multiplier: Multiplier for font sizes. Optional, 1.0 is default
        :type font_multiplier: float
        """

        if weights:
            if rose_type == 'equal-radius':
                two_halves = self.two_halves_weighted
            elif rose_type == 'equal-area':
                two_halves = np.sqrt(self.two_halves_weighted)
            else:
                raise Exception('Unknown weighted rose type')
        else:
            if rose_type == 'equal-radius':
                two_halves = self.two_halves_non_weighted
            elif rose_type == 'equal-area':
                two_halves = np.sqrt(self.two_halves_non_weighted)
            else:
                raise Exception('Unknown non-weighted rose type')
            # two_halves = self.two_halves_non_weighted
        # Plot azimuth rose plot
        ax.bar(np.deg2rad(np.arange(0, 360, 10)), two_halves, width=np.deg2rad(10), bottom=0.0, color='#F7CECC',
               edgecolor='r', alpha=0.85, zorder=4)

        # Plot setup
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 360, 45), fontweight='bold')
        ax.set_rgrids(np.linspace(5, 10, num=2), angle=0, weight='black', fmt='%d%%', fontsize=7)
        ax.grid(linewidth=1, color='k')

        title_props = dict(boxstyle='square', facecolor='white', path_effects=[path_effects.withSimplePatchShadow()])
        font_size = 20
        title_x = 0.18
        title_y = 1.25
        if weights:
            ax.set_title(name + '\nWEIGHTED', x=title_x, y=title_y, fontsize=font_multiplier * font_size,
                         fontweight='heavy'
                         , fontfamily='Times New Roman', bbox=title_props, va='top')
        else:
            ax.set_title(name, x=title_x, y=title_y, fontsize=font_multiplier * font_size, fontweight='heavy'
                         , fontfamily='Times New Roman', bbox=title_props, va='center')
        props = dict(boxstyle='round', facecolor='wheat', path_effects=[path_effects.withSimplePatchShadow()])

        text_x = 0.55
        text_y = 1.42
        text = 'n = ' + str(len(self.lineframe_main)) + '\n'
        text = text + tools.create_azimuth_set_text(self.lineframe_main)
        ax.text(text_x, text_y, text, transform=ax.transAxes, fontsize=font_multiplier * 20, weight='roman'
                , bbox=props, fontfamily='Times New Roman', va='top')
        # TickLabels
        labels = ax.get_xticklabels()
        for label in labels:
            label._y = -0.05
            label._fontproperties._size = 24
            label._fontproperties._weight = 'bold'

    def plot_azimuth_exp(self, rose_type, save=False, savefolder=None, branches=False, big_plots=False
                         , ax=None, ax_w=None):
        """

        :param rose_type: Whether to plot equal-radius or equal-area rose plot: 'equal-radius' or 'equal-area'
        :type rose_type: str
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        :param branches: Branches or traces
        :type branches: bool
        :param big_plots: Plotting to a big plot or to an individual one
        :type big_plots: bool
        :param ax: Ax to plot to
        :type ax: matplotlib.projections.polar.PolarAxes
        :param ax_w: Weighted azimuth ax to plot to
        :type ax_w: matplotlib.projections.polar.PolarAxes
        """
        if big_plots:

            self.plot_azimuth_ax_exp(ax=ax, name=self.name, weights=False, rose_type=rose_type, font_multiplier=0.5)
            self.plot_azimuth_ax_exp(ax=ax_w, name=self.name, weights=True, rose_type=rose_type, font_multiplier=0.5)

        else:
            # Non-weighted
            fig, ax = plt.subplots(subplot_kw=dict(polar=True), constrained_layout=True, figsize=(6.5, 5.1))
            self.plot_azimuth_ax_exp(ax=ax, name=self.name, weights=False, rose_type=rose_type, font_multiplier=1)

            if save:
                if branches:
                    savename = Path(savefolder + '/{}_exp_azimuth_branches.png'.format(self.name))
                else:
                    savename = Path(savefolder + '/{}_exp_azimuth_traces.png'.format(self.name))
                plt.savefig(savename, dpi=150)
            # Weighted
            fig, ax_w = plt.subplots(subplot_kw=dict(polar=True), constrained_layout=True, figsize=(6.5, 5.1))
            self.plot_azimuth_ax_exp(ax=ax_w, name=self.name, weights=True, rose_type=rose_type, font_multiplier=1)
            if save:
                if branches:
                    savename = Path(savefolder + '/{}_exp_azimuth_branches_WEIGHTED.png'.format(self.name))
                else:
                    savename = Path(savefolder + '/{}_exp_azimuth_traces_WEIGHTED.png'.format(self.name))
                plt.savefig(savename, dpi=150)

    def plot_azimuth_ax_exp(self, ax, name, weights, rose_type, font_multiplier=1.0):
        """
        EXPERIMENTAL
        :param ax: Polar axis to plot to.
        :type ax: matplotlib.projections.polar.PolarAxes
        :param name: Name used
        :type name: str
        :param weights: Whether to weight or not
        :type weights: bool
        :param rose_type: Whether to plot equal-radius or equal-area rose plot e.g. 'equal-radius' or 'equal-area'
        :type rose_type: str
        :param font_multiplier: Multiplier for font sizes. Optional, 1.0 is default
        :type font_multiplier: float
        """

        if rose_type == 'equal-radius':
            number_of_azimuths = self.number_of_azimuths
        elif rose_type == 'equal-area':
            number_of_azimuths = np.sqrt(self.number_of_azimuths)
        else:
            raise Exception('Unknown weighted rose type')
        # if weights:
        #     if rose_type == 'equal-radius':
        #         two_halves = self.two_halves_weighted
        #     elif rose_type == 'equal-area':
        #         two_halves = np.sqrt(self.two_halves_weighted)
        #     else:
        #         raise Exception('Unknown weighted rose type')
        # else:
        #     if rose_type == 'equal-radius':
        #         two_halves = self.two_halves_non_weighted
        #     elif rose_type == 'equal-area':
        #         two_halves = np.sqrt(self.two_halves_non_weighted)
        #     else:
        #         raise Exception('Unknown non-weighted rose type')
        # two_halves = self.two_halves_non_weighted

        # Plot azimuth rose plot
        ax.bar(np.deg2rad(self.bin_locs), number_of_azimuths, width=np.deg2rad(self.bin_width), bottom=0.0,
               color='#F7CECC',
               edgecolor='r', alpha=0.85, zorder=4)

        # Plot setup
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 181, 45), fontweight='bold')
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_rgrids(np.linspace(np.sqrt(number_of_azimuths).mean(), np.sqrt(number_of_azimuths).max() * 1.05, num=2),
                      angle=0, weight='black', fmt='%d', fontsize=7)
        ax.grid(linewidth=1, color='k')

        title_props = dict(boxstyle='square', facecolor='white', path_effects=[path_effects.withSimplePatchShadow()])
        font_size = 20
        title_x = 0.18
        title_y = 1.25
        if weights:
            ax.set_title(name + '\nWEIGHTED', x=title_x, y=title_y, fontsize=font_multiplier * font_size,
                         fontweight='heavy'
                         , fontfamily='Times New Roman', bbox=title_props, va='top')
        else:
            ax.set_title(name, x=title_x, y=title_y, fontsize=font_multiplier * font_size, fontweight='heavy'
                         , fontfamily='Times New Roman', bbox=title_props, va='center')
        props = dict(boxstyle='round', facecolor='wheat', path_effects=[path_effects.withSimplePatchShadow()])

        text_x = 0.55
        text_y = 1.42
        # TODO: Reimplement
        text = 'n = ' + str(len(self.lineframe_main)) + '\n'
        text = text + tools.create_azimuth_set_text(self.lineframe_main)
        ax.text(text_x, text_y, text, transform=ax.transAxes, fontsize=font_multiplier * 9, weight='roman'
                , bbox=props, fontfamily='Times New Roman', va='top')
        # TickLabels
        labels = ax.get_xticklabels()
        for label in labels:
            label._y = -0.05
            label._fontproperties._size = 24
            label._fontproperties._weight = 'bold'

    def plot_azimuth_weighted(self, rose_type, set_visualization):
        """
        Plot weighted azimuth rose-plot. Type can be 'equal-radius' or 'equal-area'
        :param rose_type: Whether to plot equal-radius or equal-area rose plot: 'equal-radius' or 'equal-area'
        :type rose_type: str
        :param set_visualization: Whether to visualize sets into the same plot
        :type set_visualization: bool
        """
        fig, ax = plt.subplots(subplot_kw=dict(polar=True), figsize=(6.5, 5.1))
        self.plot_azimuth_ax_weighted(set_visualization=set_visualization, ax=ax, name=self.name, rose_type=rose_type)

    def plot_azimuth_ax_weighted(self, set_visualization, ax, name, rose_type):
        """
        Plot weighted azimuth rose-plot to given ax. Type can be 'equal-radius' or 'equal-area'
        :param set_visualization: Whether to visualize sets into the same plot
        :type set_visualization: bool
        :param ax: Polar axis to plot on.
        :type ax: matplotlib.projections.polar.PolarAxes
        :param name: Name of the target area or group
        :type name: str
        :param rose_type: Type can be 'equal-radius' or 'equal-area'
        :type rose_type: str
        """

        if rose_type == 'equal-radius':
            number_of_azimuths = self.number_of_azimuths
        elif rose_type == 'equal-area':
            number_of_azimuths = np.sqrt(self.number_of_azimuths)
        else:
            raise Exception('Unknown weighted rose type')

        # Plot azimuth rose plot
        ax.bar(np.deg2rad(self.bin_locs), number_of_azimuths, width=np.deg2rad(self.bin_width), bottom=0.0,
               color='darkgrey',
               edgecolor='k', alpha=0.85, zorder=4)

        # Plot setup
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        ax.set_thetagrids(np.arange(0, 181, 45), fontweight='bold', fontfamily='Calibri', fontsize=11, alpha=0.95)
        ax.set_thetamin(0)
        ax.set_thetamax(180)
        ax.set_rgrids(radii=[number_of_azimuths.mean()],
                                        angle=0, fmt='', fontsize=1, alpha=0.8, ha='left')
        ax.grid(linewidth=1, color='k', alpha=0.8)

        # Title is the name of the target area or group
        prop_title = dict(boxstyle='square', facecolor='linen', alpha=1, linewidth=2)
        ax.set_title(f'   {name}   ', x=0.94, y=0.8,
                     fontsize=20, fontweight='bold', fontfamily='Calibri'
                     , va='top', bbox=prop_title, transform=ax.transAxes, ha='center')

        # Fractions of length for each set
        prop = dict(boxstyle='square', facecolor='linen', alpha=1, pad=0.45)
        text = 'n = ' + str(len(self.lineframe_main)) + '\n'
        text = text + tools.create_azimuth_set_text(self.lineframe_main)
        ax.text(0.94, 0.3, text, transform=ax.transAxes, fontsize=12, weight='roman'
                , bbox=prop, fontfamily='Calibri', va='top', ha='center')

        # TickLabels
        labels = ax.get_xticklabels()
        for label in labels:
            label._y = -0.01
            label._fontproperties._size = 15
            label._fontproperties._weight = 'bold'
        # Set ranges visualized if set_visualization is True
        if set_visualization:
            for _, row in self.set_df.iterrows():
                set_range = row.SetLimits
                if set_range[0] < set_range[1]:
                    diff = set_range[1] - set_range[0]
                    set_loc = set_range[0] + diff / 2
                else:
                    diff = 360 - set_range[0] + set_range[1]
                    if 180 - set_range[0] > set_range[1]:
                        set_loc = set_range[0] + diff / 2
                    else:
                        set_loc = set_range[1] - diff / 2

                ax.bar([np.deg2rad(set_loc)], [number_of_azimuths.mean()], width=np.deg2rad(diff), bottom=0.0,
                       alpha=0.5, label=f'Set {row.Set}')
                ax.legend(loc=(-0.02, 0.41), edgecolor='black'
                          , prop={'family': 'Calibri', 'size': 12})

    def topology_parameters_2d_branches(self, branches=False):
        """
        Gather topology parameters for branch data.
        :param branches: Branches or traces
        :type branches: bool
        """
        # SAME METHOD FOR BOTH TRACES AND BRANCHES.
        # MAKE SURE YOU KNOW WHICH YOU ARE USING.
        fracture_intensity = self.lineframe_main.length.sum() / self.area
        aerial_frequency = len(self.lineframe_main) / self.area
        characteristic_length = self.lineframe_main.length.mean()
        dimensionless_intensity = fracture_intensity * characteristic_length
        number_of_lines = len(self.lineframe_main)
        if branches:
            try:
                connection_dict = self.lineframe_main.Connection.value_counts().to_dict()
            except AttributeError:
                raise AttributeError('branches=True BUT given lineframe doesnt contain branch attributes.')
            if connection_dict['C - C'] == 0:
                print('*************WARNING*************')
                print('Connection dictionary had no C - C branches...')
                print('IN METHOD: topology_parameters_2d_branches')
                print('*************WARNING*************')
            return fracture_intensity, aerial_frequency, characteristic_length, dimensionless_intensity, number_of_lines, connection_dict
        else:
            return fracture_intensity, aerial_frequency, characteristic_length, dimensionless_intensity, number_of_lines

    def plot_branch_ternary_point(self, tax):

        """
        Plot a branch classification ternary plot to a tax
        :param tax: python-ternary AxesSubPlot
        :type tax: ternary.TernaryAxesSubplot
        :return:
        :rtype:
        """
        connection_dict = self.lineframe_main.Connection.value_counts().to_dict()
        name = self.name
        cc = connection_dict['C - C']
        ci = connection_dict['C - I']
        ii = connection_dict['I - I']
        sumcount = cc + ci + ii
        ccp = 100 * cc / sumcount
        cip = 100 * ci / sumcount
        iip = 100 * ii / sumcount

        point = [(ccp, iip, cip)]
        tax.scatter(point, marker='X', color='black', alpha=1, zorder=3, s=175)
        tax.scatter(point, marker='x', label=name, alpha=1, zorder=4, s=100)

    # def calc_ellipse_weights(self, a, b, phi):
    #     self.lineframe_main = tools.calc_ellipse_weight(self.lineframe_main, a, b, phi)
    #     self.rep_circle_area = np.pi * b ** 2
    #     self.rep_circle_r = b

    def calc_anisotropy(self):
        """
        Calculates annisotropy of connectivity for branch DataFrame
        :return:
        :rtype:
        """
        branchframe = self.lineframe_main

        branchframe['anisotropy'] = branchframe.apply(
            lambda row: tools.aniso_calc_anisotropy(row['halved'], row['Connection'], row['length']),
            axis=1)
        arr_sum = branchframe.anisotropy.sum()

        self.anisotropy = arr_sum
        # self.anisotropy_div_area = arr_sum / self.rep_circle_area

    def plot_anisotropy_styled(self, for_ax=False, ax=None, save=False, save_folder=None):
        """
        Plots a styled anisotropy of connectivity figure
        :param for_ax: Whether plotting to a ready-made ax or not
        :type for_ax: bool
        :param ax: ax to plot to (optional)
        :type ax: matplotlib.axes.Axes
        :param save: Whether to save
        :type save: bool
        :param save_folder: Folder to save to
        :type save_folder: str
        :return:
        :rtype:
        """
        double_anisotropy = list(self.anisotropy) + list(self.anisotropy)
        angles_of_study = config.angles_for_examination
        opp_angles = [i + 180 for i in angles_of_study]
        angles = list(angles_of_study) + opp_angles
        if for_ax:
            pass
        else:
            fig, ax = plt.subplots(subplot_kw=dict(polar=True))

        # PLOT SETUP
        ax.set_theta_zero_location('N')
        ax.set_theta_direction(-1)
        max_aniso = max(self.anisotropy)

        for theta, r in zip(angles, double_anisotropy):
            theta = np.deg2rad(theta)
            ax.annotate('', xy=(theta, r), xytext=(theta, 0)
                        , arrowprops=dict(edgecolor='black', facecolor='seashell', shrink=0.03, linewidth=1.5))
        ax.scatter([np.deg2rad(angles_value) for angles_value in angles], double_anisotropy
                   , marker='o', c='black', zorder=9, s=20)
        # NO AXES
        ax.axis('off')
        # CREATE CURVED STRUCTURE AROUND SCATTER AND ARROWS
        angles.append(359.999)
        double_anisotropy.append((double_anisotropy[0]))
        angles = np.array(angles)
        double_anisotropy = np.array(double_anisotropy)
        # INTERPOLATE BETWEEN CALCULATED POINTS
        xnew = np.linspace(angles.min(), angles.max(), 300)
        spl = make_interp_spline(angles, double_anisotropy, k=3)
        power_smooth = spl(xnew)
        ax.plot(np.deg2rad(xnew), power_smooth, linewidth=1.5)
        circle = patches.Circle((0, 0), 0.05 * max_aniso, transform=ax.transData._b, edgecolor='black',
                                facecolor='gray', zorder=10)
        ax.add_artist(circle)
        if not for_ax:
            if save:
                name = self.name
                savename = Path(save_folder + '/{}_anisotropy_indiv.png'.format(name))
                plt.savefig(savename, dpi=150)


class TargetAreaNodes:
    def __init__(self, nodeframe, name, group):
        """
        Init of TargetAreaNodes
        :param nodeframe: DataFrame with node data
        :type nodeframe: gpd.GeoDataFrame
        :param name: Name of the target area
        :type name: str
        :param group: Group of the target area
        :type group: str
        """
        self.nodeframe = nodeframe
        self.name = name
        self.group = group

    def plot_xyi(self, save=False, savefolder=None, for_ax=False, ax=None):
        """
        Plot a single XYI-ternary figure to ready-made ax or its own
        :param save: Whether to save
        :type save: bool
        :param savefolder: Folder to save to
        :type savefolder: str
        :param for_ax: Whether plotting to a ready-made ax or not
        :type for_ax: bool
        :param ax: ax to plot to (optional)
        :type ax: matplotlib.axes.Axes
        :return:
        :rtype:
        """
        if for_ax:
            pass
        else:
            fig, ax = plt.subplots(figsize=(7, 7))
        tools.plot_ternary_xyi_subplot(self.nodeframe, ax=ax, name=self.name)
        if save:
            name = self.name
            savename = Path(savefolder + '/{}_xyi.png'.format(name))
            plt.savefig(savename, dpi=150)

    def plot_xyi_point(self, tax):
        """
        Plot XYI-point into a ready-made ternary axis
        :param tax: python-ternary AxesSubPlot
        :type tax: ternary.TernaryAxesSubplot
        :return:
        :rtype:
        """
        tools.plot_ternary_xyi_point(self.nodeframe, tax, name=self.name)

    def topology_parameters_2d_nodes(self):
        """
        Gathers topology parameters of nodes
        :return:
        :rtype:
        """
        nodeframe = self.nodeframe
        node_dict = nodeframe.c.value_counts().to_dict()
        return node_dict
