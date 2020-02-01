# Python Windows co-operation imports
from pathlib import Path

import matplotlib.patches as patches
# Math and analysis imports
# Plotting imports
# DataFrame analysis imports
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import geopandas as gpd
import seaborn as sns
from scipy.interpolate import make_interp_spline
import ternary
import logging

# Own code imports
from . import tools
from . import templates
from ... import fracture_analysis_2d


# Classes

class TargetAreaLines:
    # TODO: Add using_branches to ld as well?
    def __init__(self, lineframe, areaframe, name, group, using_branches: bool, cut_off=1.0):
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

    def calc_attributes(self):
        self.lineframe_main = self.lineframe.sort_values(by=['length'], ascending=False)
        self.lineframe_main = tools.calc_y_distribution(self.lineframe_main, self.area)

        self.lineframe_main['azimu'] = self.lineframe_main.geometry.apply(tools.calc_azimu)
        # TODO: TEST AND UNDERSTAND WHY THERE ARE nan in AZIMU CALC
        self.lineframe_main = self.lineframe_main.dropna(subset=['azimu'])
        self.lineframe_main['halved'] = self.lineframe_main.azimu.apply(tools.azimu_half)

        self.cut_off_length = tools.calc_cut_off_length(self.lineframe_main, self.cut_off)

        # Allows plotting of azimuth
        self.two_halves = tools.azimuth_plot_attributes(self.lineframe_main, weights=False)
        # Length distribution plot limits
        self.left, self.right = tools.calc_xlims(self.lineframe_main)
        self.top, self.bottom = tools.calc_ylims(self.lineframe_main)

        self.lineframe_main_cut = self.lineframe_main.loc[self.lineframe_main['length'] >= self.cut_off_length]
        # Reinforce numeric columns

        logger = logging.getLogger('logging_tool')
        logger.info('self.lineframe_main\n\n{}'.format(self.lineframe_main))
        logger.info('self.lineframe_main dtypes\n\n{}'.format(self.lineframe_main.dtypes))
        logger.info('self.lineframe_main_cut\n\n{}'.format(self.lineframe_main_cut))
        logger.info('self.lineframe_main_cut dtypes\n\n{}'.format(self.lineframe_main_cut.dtypes))


    def calc_curviness(self):
        self.lineframe_main['curviness'] = self.lineframe_main.geometry.apply(tools.curviness)

    def plot_length_distribution(self, save=False, savefolder=None):
        fig, ax = plt.subplots()
        self.plot_length_distribution_ax(ax)
        tools.setup_ax_for_ld(ax, self, font_multiplier=0.5)
        if save:
            name = self.name
            savename = Path(savefolder + '/{}_indiv_full.png'.format(name))
            plt.savefig(savename, dpi=150)

    def plot_length_distribution_ax(self, ax, cut=False, use_sets=False, curr_set=-1):
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
            lineframe_cut.plot.scatter(x='length', y='y', logx=True, logy=True, label=self.name + '_cut', ax=ax, color='black')

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

    # list_of_tuples, tuples must be between 0-180
    def define_sets(self, list_of_tuples=((0, 60), (60, 120), (120, 180))):
        self.lineframe_main['set'] = self.lineframe_main.apply(lambda x: tools.define_set(x['halved'], list_of_tuples)
                                                               , axis=1)
        self.lineframe_main_cut['set'] = self.lineframe_main_cut.apply(
            lambda x: tools.define_set(x['halved'], list_of_tuples)
            , axis=1)
        self.set_list = list_of_tuples

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

    def plot_azimuth(self, save=False, savefolder=None, branches=False, big_plots=False, ellipse_weights=False
                     , ax=None, ax_w=None, ax_ew=None, small_text=False):
        if big_plots:
            if ellipse_weights:
                tools.plot_azimuths_sub_plot(self.lineframe_main, ax=ax_ew, filename=self.name, weights=False,
                                             small_text=small_text)
            else:
                tools.plot_azimuths_sub_plot(self.lineframe_main, ax=ax, filename=self.name, weights=False,
                                             small_text=small_text)
                tools.plot_azimuths_sub_plot(self.lineframe_main, ax=ax_w, filename=self.name, weights=True,
                                             small_text=small_text)

        else:
            fig, ax = plt.subplots(subplot_kw=dict(polar=True), constrained_layout=True, figsize=(6.5, 5.1))
            tools.plot_azimuths_sub_plot(self.lineframe_main, ax=ax, filename=self.name, weights=False,
                                         small_text=small_text)
            if save:
                if branches:
                    savename = Path(savefolder + '/{}_azimuth_branches.png'.format(self.name))
                else:
                    savename = Path(savefolder + '/{}_azimuth_traces.png'.format(self.name))
                plt.savefig(savename, dpi=150)
            fig, ax = plt.subplots(subplot_kw=dict(polar=True), constrained_layout=True, figsize=(6.5, 5.1))
            tools.plot_azimuths_sub_plot(self.lineframe_main, ax=ax, filename=self.name, weights=True,
                                         small_text=small_text)
            if save:
                if branches:
                    savename = Path(savefolder + '/{}_azimuth_branches_WEIGHTED.png'.format(self.name))
                else:
                    savename = Path(savefolder + '/{}_azimuth_traces_WEIGHTED.png'.format(self.name))
                plt.savefig(savename, dpi=150)
            if ellipse_weights:
                fig, ax = plt.subplots(subplot_kw=dict(polar=True), constrained_layout=True, figsize=(6.5, 5.1))
                tools.plot_azimuths_sub_plot(self.lineframe_main, ax=ax, filename=self.name, weights=False,
                                             small_text=small_text)
                if save:
                    if branches:
                        savename = Path(savefolder + '/{}_azimuth_branches_ELLIPSE_WEIGHTED.png'.format(self.name))
                    else:
                        savename = Path(savefolder + '/{}_azimuth_traces_ELLIPSE_WEIGHTED.png'.format(self.name))
                    plt.savefig(savename, dpi=150)

    def topology_parameters_2d_branches(self, branches=False):
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
        try:
            tax.scatter(point, marker='x', color=templates.color_dict[name], label=name, alpha=1, zorder=4, s=100)
        except KeyError:
            tax.scatter(point, marker='x', label=name, alpha=1, zorder=4, s=100)

    # def calc_ellipse_weights(self, a, b, phi):
    #     self.lineframe_main = tools.calc_ellipse_weight(self.lineframe_main, a, b, phi)
    #     self.rep_circle_area = np.pi * b ** 2
    #     self.rep_circle_r = b

    def calc_anisotropy(self):
        branchframe = self.lineframe_main

        branchframe['anisotropy'] = branchframe.apply(
            lambda row: tools.aniso_calc_anisotropy(row['halved'], row['Connection'], row['length']),
            axis=1)
        arr_sum = branchframe.anisotropy.sum()

        self.anisotropy = arr_sum
        # self.anisotropy_div_area = arr_sum / self.rep_circle_area

    def plot_anisotropy_styled(self, for_ax=False, ax=None, save=False, save_folder=None):
        double_anisotropy = list(self.anisotropy) + list(self.anisotropy)
        angles_of_study = templates.angles_for_examination
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
        self.nodeframe = nodeframe
        self.name = name
        self.group = group



    def plot_xyi(self, save=False, savefolder=None, for_ax=False, ax=None):
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
        tools.plot_ternary_xyi_point(self.nodeframe, tax, name=self.name)

    def topology_parameters_2d_nodes(self):
        nodeframe = self.nodeframe
        node_dict = nodeframe.c.value_counts().to_dict()
        return node_dict
