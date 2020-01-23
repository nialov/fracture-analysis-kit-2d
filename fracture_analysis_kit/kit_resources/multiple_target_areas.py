# Python Windows co-operation imports
from pathlib import Path

# Math and analysis imports
# Plotting imports
# DataFrame analysis imports
import geopandas as gpd
import matplotlib.patheffects as path_effects
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import ternary
from matplotlib.ticker import FormatStrFormatter
import shapely

# Own code imports
from . import templates
from . import tools


# import kit_resources.templates as templates  # Contains plotting templates
# import kit_resources.tools as tools  # Main tool/helper module


class MultiTargetArea:

    def __init__(self, linedirs, areadirs, nodedirs, codes, cut_offs, branches):
        # length distribution setup
        self.linedirs = linedirs
        self.areadirs = areadirs
        self.codes = codes
        self.cut_offs = cut_offs  # cut_offs structure [[m20,det], [m20, det], [lidar], [lidar]]
        # node data setup
        self.nodedirs = nodedirs
        self.using_branches = branches
        self.df = pd.DataFrame(columns=['filename', 'lineframe', 'areaframe', 'nodeframe', 'code', 'cut_off'])

        # Assign None to later initialized attributes
        # TODO: TEST PROPERLY
        self.set_list = None
        self.uniframe = None
        self.uniframe_lineframe_main_concat = None
        self.uni_left, self.uni_right, self.uni_top, self.uni_bottom = None, None, None, None
        self.relations_set_counts = None
        self.xy_relations_frame = None
        self.xy_relations_frame_indiv = None
        self.relations_set_counts = None
        self.uniframe_topology_concat = None
        self.relations_set_counts_indiv = None

        for code, cut_off_l in zip(self.codes, self.cut_offs):
            lfs, afs, nfs = [], [], []
            for linedir, areadir, nodedir in zip(self.linedirs, self.areadirs, self.nodedirs):
                # TODO: Big assumption is made here: All files can be ordered alphabetically...
                linefiles, areafiles = tools.get_filenames_branches_traces_and_areas_coded(linedir, areadir, code)
                nodefiles = tools.get_filenames_nodes_coded_excp(nodedir, code)
                # print(linefiles, areafiles, nodefiles)  # DEBUGGING

                lfs.extend(linefiles)
                afs.extend(areafiles)
                nfs.extend(nodefiles)

            for linefile, areafile, nodefile in zip(lfs, afs, nfs):

                if 'Detailed' in linefile:
                    if len(cut_off_l) > 1:
                        cut_off = cut_off_l[1]
                    else:
                        cut_off = cut_off_l[0]
                    code_temp = code + '_det'
                elif '20m' in linefile:
                    cut_off = cut_off_l[0]
                    code_temp = code + '_20m'
                elif 'LiDAR_' in linefile:
                    cut_off = cut_off_l[0]
                    code_temp = code + '_LiDAR'

                else:
                    cut_off = cut_off_l[0]
                    code_temp = code + '_UNKNOWN_ERROR'

                filename = linefile
                lineframe = tools.initialize_trace_frame(linefile)
                areaframe = tools.initialize_area_frame(areafile)
                nodeframe = tools.initialize_node_frame(nodefile)

                appendage = {'filename': filename, 'lineframe': lineframe,
                             'areaframe': areaframe,
                             'nodeframe': nodeframe,
                             'code': code_temp,
                             'cut_off': cut_off}
                self.df = self.df.append(appendage, ignore_index=True)

        self.norm_list = tools.get_area_normalisations_frames(self.df.areaframe.tolist())
        norm_array = np.asarray(self.norm_list)
        self.df['norm'] = norm_array
        self.df['TargetAreaLines'] = self.df.apply(
            lambda x: tools.construct_length_distribution_base(x['lineframe'], x['areaframe'], x['code'], x['cut_off'],
                                                               x['norm'], x['filename'], self.using_branches), axis=1)
        self.df['TargetAreaNodes'] = self.df.apply(
            lambda x: tools.construct_node_data_base(x['nodeframe'], x['code'], x['filename']), axis=1)

    def calc_attributes_for_all(self):
        for idx, row in self.df.iterrows():
            row['TargetAreaLines'].calc_attributes()

    def define_sets_for_all(self, list_of_tuples):
        # TODO: Implement sets
        if list_of_tuples is None:
            list_of_tuples = [(0, 60), (60, 120), (120, 180)]
        self.set_list = list_of_tuples
        for idx, row in self.df.iterrows():
            row['TargetAreaLines'].define_sets(list_of_tuples)

    def calc_curviness_for_all(self, use_branches_anyway=False):
        if use_branches_anyway:
            pass
        elif self.using_branches:
            raise Exception('Not recommended for branch data.')
        for idx, row in self.df.iterrows():
            row['TargetAreaLines'].calc_curviness()

    # def calc_ellipse_weights_for_all(self, representative_ellipses):
    #     self.representative_ellipses = representative_ellipses
    #     for idx, row in self.df.iterrows():
    #         for item in representative_ellipses.items():
    #             if item[0] in row.filename:
    #                 # print(item[0], row.filename) DEBUGGING
    #                 a = item[1][1]
    #                 b = item[1][2]
    #                 phi = item[1][3]
    #                 # TODO: Do this right..
    #                 phi = 90 - phi
    #                 row.TargetAreaLines.calc_ellipse_weights(a, b, phi)

    def plot_curviness_for_unified(self, violins=False, save=False, savefolder=None):
        if violins:
            for idx, row in self.uniframe.iterrows():
                row['uni_ld'].plot_curviness_violins()
                if save:
                    savename = Path(savefolder + '/{}_curviness_violin'.format(row['code']))
                    plt.savefig(savename, dpi=150)
        else:
            for idx, row in self.uniframe.iterrows():
                row['uni_ld'].plot_curviness()
                if save:
                    savename = Path(savefolder + '/{}_curviness_box'.format(row['code']))
                    plt.savefig(savename, dpi=150)

    def unified(self):
        uniframe = pd.DataFrame(columns=['uni_ld', 'uni_nd', 'code', 'uni_ld_area', 'uni_rep_circles_area'])
        for idx, code in enumerate(self.codes):
            # TODO: This code shit should be (fixed), now to implement!
            # frame_debug = self.df.loc[self.df['code'].str.contains(code)]
            # # Code should represent part before a '_' symbol
            frame = self.df.loc[self.df['code'].str.contains(code)]

            # if not frame.equals(frame_debug):  # DEBUGGING
            #     print(code, frame.head(), frame_debug.head())  # DEBUGGING
            #     raise Exception('Given code doesnt represent the part before a "_" symbol. CHECK GIVEN CODES!')
            det_frame = frame.loc[frame['code'].str.contains('_det')]
            m20_frame = frame.loc[frame['code'].str.contains('_20m')]
            lidar_frame = frame.loc[frame['code'].str.contains('_LiDAR')]
            if len(det_frame) > 0:
                temp_code = code + '_det'
                unif_ld_main = tools.unify_lds(det_frame.TargetAreaLines.tolist())
                unif_ld_main.calc_attributes()
                uni_ld_area = gpd.GeoDataFrame(pd.concat(det_frame.areaframe.tolist(), ignore_index=True))
                unif_nd_main = tools.unify_nds(det_frame.TargetAreaNodes.tolist())
                uniframe = uniframe.append(
                    {'uni_ld': unif_ld_main, 'uni_nd': unif_nd_main, 'code': temp_code, 'uni_ld_area': uni_ld_area},
                    ignore_index=True)
            if len(m20_frame) > 0:
                temp_code = code + '_20m'
                unif_ld_main = tools.unify_lds(m20_frame.TargetAreaLines.tolist())
                unif_ld_main.calc_attributes()
                uni_ld_area = gpd.GeoDataFrame(pd.concat(m20_frame.areaframe.tolist(), ignore_index=True))
                unif_nd_main = tools.unify_nds(m20_frame.TargetAreaNodes.tolist())
                uniframe = uniframe.append(
                    {'uni_ld': unif_ld_main, 'uni_nd': unif_nd_main, 'code': temp_code, 'uni_ld_area': uni_ld_area},
                    ignore_index=True)
            if len(lidar_frame) > 0:
                temp_code = code + '_LiDAR'
                unif_ld_main = tools.unify_lds(lidar_frame.TargetAreaLines.tolist())
                unif_ld_main.calc_attributes()
                uni_ld_area = gpd.GeoDataFrame(pd.concat(lidar_frame.areaframe.tolist(), ignore_index=True))
                unif_nd_main = tools.unify_nds(lidar_frame.TargetAreaNodes.tolist())
                uniframe = uniframe.append(
                    {'uni_ld': unif_ld_main, 'uni_nd': unif_nd_main, 'code': temp_code, 'uni_ld_area': uni_ld_area},
                    ignore_index=True)

        uniframe = tools.norm_unified(uniframe)
        self.uniframe = uniframe
        # AIDS FOR PLOTTING:
        self.uniframe_lineframe_main_concat = pd.concat([srs.lineframe_main for srs in self.uniframe.uni_ld], sort=True)
        self.uni_left, self.uni_right = tools.calc_xlims(self.uniframe_lineframe_main_concat)
        self.uni_top, self.uni_bottom = tools.calc_ylims(self.uniframe_lineframe_main_concat)

    def create_setframes_for_all_unified(self):
        for idx, row in self.uniframe.iterrows():
            row['uni_ld'].create_setframes()

    def plot_lengths_all(self, save=False, savefolder=None):
        for idx, srs in self.df.iterrows():
            srs['TargetAreaLines'].plot_length_distribution(save=save, savefolder=savefolder)

    def plot_lengths_unified(self, use_sets=False):
        for idx, srs in self.uniframe.iterrows():
            srs['uni_ld'].plot_length_distribution()
        if use_sets:
            # TODO: reimplement
            raise Exception('use_sets Not implemented')
            # for idx, srs in self.uniframe.iterrows():
            #     srs['uni_ld'].plot_length_distribution(use_sets=True)

    def plot_lengths_unified_combined(self, use_sets=False, save=False, savefolder=None, logarithmic=True):
        figure_size = (16, 16)

        props = dict(boxstyle='round', pad=1, facecolor='wheat',
                     path_effects=[path_effects.SimplePatchShadow(), path_effects.Normal()])

        fig, ax = plt.subplots(figsize=figure_size)  # Figure for full LDs
        #        length_text = 'FULL'+'\nCut Off Lengths (m)\n\n'
        if logarithmic:
            ax.set_xlim(self.uni_left, self.uni_right)
            ax.set_ylim(self.uni_bottom, self.uni_top)
        else:
            pass
        for idx, srs in self.uniframe.iterrows():
            srs['uni_ld'].plot_length_distribution_ax(ax=ax, logarithmic=logarithmic)

        tools.setup_ax_for_ld(ax, self, unified=True, font_multiplier=1, logarithmic=logarithmic, predictions=False)
        if save:
            savename = Path(savefolder + '/FULL_LD.png')
            plt.savefig(savename, dpi=150)
        fig, ax = plt.subplots(figsize=figure_size)  # Figure for CUT LDs
        length_text = 'CUT' + '\nCut Off Lengths (m)\n\n'
        for idx, srs in self.uniframe.iterrows():
            srs['uni_ld'].plot_length_distribution_ax(ax=ax, cut=True, logarithmic=logarithmic)
            min_length = srs['uni_ld'].lineframe_main_cut.length.min()
            code = srs['code']
            length_text = length_text + code + ' : ' + str(round(min_length, 2)) + '\n'
        if logarithmic:
            tools.plot_fit_for_uniframe(self, ax=ax, cut=True, use_sets=False)
        else:
            pass

        tools.setup_ax_for_ld(ax, self, unified=True, font_multiplier=1, logarithmic=logarithmic)
        ax.text(0.1, 0.25, length_text, transform=ax.transAxes, fontsize=28, weight='roman', verticalalignment='center',
                bbox=props, fontfamily='Times New Roman')
        if save:
            savename = Path(savefolder + '/CUT_LD_WITH_FIT.png')
            plt.savefig(savename, dpi=150)

        if use_sets:
            for curr_set, s in enumerate(self.set_list):

                fig, ax = plt.subplots(figsize=figure_size)  # Figure for full LDs, for each set
                #                length_text = 'FULL, SET '+str(idx)+'\nCut Off Lengths (m)\n\n'
                for idx, srs in self.uniframe.iterrows():
                    srs['uni_ld'].plot_length_distribution_ax(ax=ax, use_sets=True, curr_set=curr_set)
                #                    min_length = srs['uni_ld'].setframes[curr_set].length.min()
                #                    code = srs['code']
                #                    length_text = length_text+code+' : '+str(round(min_length, 2))+'\n'

                tools.setup_ax_for_ld(ax, self, unified=True)
                if save:
                    savename = Path(savefolder + '/FULL_LD_SET_{}.png'.format(curr_set))
                    plt.savefig(savename, dpi=150)
                fig, ax = plt.subplots(figsize=figure_size)  # Figure for cut LDs, for each set
                length_text = 'CUT, SET ' + str(curr_set) + '\nCut Off Lengths (m)\n\n'
                for idx, srs in self.uniframe.iterrows():
                    srs['uni_ld'].plot_length_distribution_ax(ax=ax, cut=True, use_sets=True, curr_set=curr_set)
                    min_length = srs['uni_ld'].setframes_cut[curr_set].length.min()
                    code = srs['code']
                    length_text = length_text + code + ' : ' + str(round(min_length, 2)) + '\n'

                tools.plot_fit_for_uniframe(self, ax=ax, cut=True, use_sets=True, curr_set=curr_set, font_multiplier=1)

                tools.setup_ax_for_ld(ax, self, unified=True)
                ax.text(0.1, 0.3, length_text, transform=ax.transAxes, fontsize=18, weight='roman',
                        verticalalignment='top', bbox=props, fontfamily='Times New Roman')
                if save:
                    savename = Path(savefolder + '/CUT_LD_SET_{}.png'.format(curr_set))
                    plt.savefig(savename, dpi=150)

    def plot_lengths_unified_combined_predictions(self, use_sets=False, save=False, savefolder=None, predict_with=None):
        figure_size = (16, 16)

        props = dict(boxstyle='round', pad=1, facecolor='wheat',
                     path_effects=[path_effects.SimplePatchShadow(), path_effects.Normal()])

        fig, ax = plt.subplots(figsize=figure_size)  # Figure for CUT LDs
        length_text = 'Cut Off Lengths (m)\n\n'
        for idx, srs in self.uniframe.iterrows():
            srs['uni_ld'].plot_length_distribution_ax(ax=ax, cut=True, logarithmic=True)
            min_length = srs['uni_ld'].lineframe_main_cut.length.min()
            code = srs['code']
            length_text = length_text + code + ' : ' + str(round(min_length, 2)) + '\n'

        tools.plot_fit_for_uniframe(self, ax=ax, cut=True, use_sets=False, predicting_mode=True,
                                    predict_with=predict_with)
        tools.setup_ax_for_ld(ax, self, unified=True, font_multiplier=1, logarithmic=True)

        ax.text(0.1, 0.25, length_text, transform=ax.transAxes, fontsize=20, weight='roman', verticalalignment='center',
                bbox=props, fontfamily='Times New Roman')

        if save:
            savename = savefolder + '/CUT_LD_WITH_FIT_predictions'
            for pw in predict_with:
                savename = savename + '_' + pw
            savename = Path(savename + '.png')
            plt.savefig(savename, dpi=150)

        if use_sets:
            for curr_set, s in enumerate(self.set_list):

                fig, ax = plt.subplots(figsize=figure_size)  # Figure for full LDs, for each set
                #                length_text = 'FULL, SET '+str(idx)+'\nCut Off Lengths (m)\n\n'
                for idx, srs in self.uniframe.iterrows():
                    srs['uni_ld'].plot_length_distribution_ax(ax=ax, use_sets=True, curr_set=curr_set)
                #                    min_length = srs['uni_ld'].setframes[curr_set].length.min()
                #                    code = srs['code']
                #                    length_text = length_text+code+' : '+str(round(min_length, 2))+'\n'

                tools.setup_ax_for_ld(ax, self, unified=True)
                if save:
                    savename = Path(savefolder + '/FULL_LD_SET_{}_predictions.png'.format(curr_set))
                    plt.savefig(savename, dpi=150)
                fig, ax = plt.subplots(figsize=figure_size)  # Figure for cut LDs, for each set
                length_text = 'CUT, SET ' + str(curr_set) + '\nCut Off Lengths (m)\n\n'
                for idx, srs in self.uniframe.iterrows():
                    srs['uni_ld'].plot_length_distribution_ax(ax=ax, cut=True, use_sets=True, curr_set=curr_set)
                    min_length = srs['uni_ld'].setframes_cut[curr_set].length.min()
                    code = srs['code']
                    length_text = length_text + code + ' : ' + str(round(min_length, 2)) + '\n'

                tools.plot_fit_for_uniframe(self, ax=ax, cut=True, use_sets=True, curr_set=curr_set, font_multiplier=1)

                tools.setup_ax_for_ld(ax, self, unified=True)
                ax.text(0.1, 0.3, length_text, transform=ax.transAxes, fontsize=18, weight='roman',
                        verticalalignment='top', bbox=props, fontfamily='Times New Roman')
                if save:
                    savename = Path(savefolder + '/CUT_LD_SET_{}_predictions.png'.format(curr_set))
                    plt.savefig(savename, dpi=150)

    def plot_all_azimuths(self, save=False, savefolder=None, big_plots=True, small_text=False):
        if big_plots:
            plot_count = len(self.df)
            if plot_count < 5:
                plot_count = 5
            cols = 4
            if plot_count % cols == 0:
                rows = plot_count // cols
            else:
                rows = plot_count // cols + 1
            width = 26
            height = (width / cols) * (rows * 1.3)
            fig, ax = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
                                   , figsize=(width, height))
            fig_w, ax_w = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
                                       , figsize=(width, height))
            # if ellipse_weights:
            #     fig_ew, ax_ew = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
            #                                  , figsize=(width, height))
            for idx, row in self.df.iterrows():

                row['TargetAreaLines'].plot_azimuth(save=False, savefolder=savefolder, branches=self.using_branches
                                                    , big_plots=big_plots
                                                    , ax=ax[idx // cols][idx % cols]
                                                    , ax_w=ax_w[idx // cols][idx % cols]
                                                    , small_text=small_text)
            #         if ellipse_weights:
            #             row['TargetAreaLines'].plot_azimuth(save=False, savefolder=savefolder, branches=branches
            #                                                    , big_plots=big_plots
            #                                                    , ellipse_weights=ellipse_weights
            #                                                    , ax_ew=ax_ew[idx // cols][idx % cols]
            #                                                    , small_text = small_text)
            top, bottom, left, right, hspace, wspace = 0.93, 0.07, 0.05, 0.95, 0.3, 0.3
            fig.tight_layout()
            fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
            fig_w.tight_layout()
            fig_w.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
            # if ellipse_weights:
            #     fig_ew.tight_layout()
            #     fig_ew.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
            if save:
                savename = Path(savefolder + '/azimuths_all.png')
                savename_w = Path(savefolder + '/azimuths_WEIGHTED_all.png')
                fig.savefig(savename, dpi=150)
                fig_w.savefig(savename_w, dpi=150)
                # if ellipse_weights:
                #     savename_ew = Path(savefolder + '/azimuths_ELLIPSE_WEIGHTED_all.png')
                #     fig_ew.savefig(savename_ew, dpi=150)
        # elif ellipse_weights:
        #     for idx, row in self.df.iterrows():
        #         row['TargetAreaLines'].plot_azimuth(save=save, savefolder=savefolder, branches=branches
        #                                    , ellipse_weights=ellipse_weights, small_text = small_text)
        else:
            for idx, row in self.df.iterrows():
                row['TargetAreaLines'].plot_azimuth(save=save, savefolder=savefolder, branches=self.using_branches
                                                    , small_text=small_text)

    def plot_unified_azimuths(self, save=False, savefolder=None, big_plots=False):
        branches = self.using_branches
        if big_plots:
            plot_count = len(self.uniframe)
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
            # if ellipse_weights:
            #     fig_ew, ax_ew = plt.subplots(ncols=cols, nrows=rows, subplot_kw=dict(polar=True)
            #                                  , figsize=(width, height))
            for idx, row in self.uniframe.iterrows():
                row['uni_ld'].plot_azimuth(save=False, savefolder=savefolder, branches=branches
                                           , big_plots=big_plots
                                           , ax=ax[idx // cols][idx % cols]
                                           , ax_w=ax_w[idx // cols][idx % cols])
                # if ellipse_weights:
                #     row['uni_ld'].plot_azimuth(save=False, savefolder=savefolder, branches=branches
                #                                , big_plots=big_plots
                #                                , ellipse_weights=ellipse_weights
                #                                , ax_ew=ax_ew[idx // cols][idx % cols])

            top, bottom, left, right, hspace, wspace = 0.90, 0.07, 0.05, 0.95, 0.3, 0.3
            fig.tight_layout()
            fig.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
            fig_w.tight_layout()
            fig_w.subplots_adjust(top=top, bottom=bottom, left=left, right=right, hspace=hspace, wspace=wspace)
            # if ellipse_weights:
            #     fig_ew.tight_layout()
            #     fig_ew.subplots_adjust(top=0.93, bottom=0.07, left=0.08, right=0.92, hspace=0.25, wspace=0.3)
            if save:
                savename = Path(savefolder + '/azimuths_unified_all.png')
                savename_w = Path(savefolder + '/azimuths_unified_WEIGHTED_all.png')
                fig.savefig(savename, dpi=150)
                fig_w.savefig(savename_w, dpi=150)
                # if ellipse_weights:
                #     savename_ew = Path(savefolder + '/azimuths_unified_ELLIPSE_WEIGHTED_all.png')
                #     fig_ew.savefig(savename_ew, dpi=150)
        # elif ellipse_weights:
        #     for idx, row in self.uniframe.iterrows():
        #         row['uni_ld'].plot_azimuth(save=save, savefolder=savefolder, branches=branches
        #                                    , ellipse_weights=ellipse_weights)
        else:
            for idx, row in self.uniframe.iterrows():
                row['uni_ld'].plot_azimuth(save=save, savefolder=savefolder, branches=branches)

    def determine_xy_relations_unified(self, big_plot=True):
        # Determines xy relations and dynamically creates a dataframe as an aid for plotting the relations
        # TODO: No within set relations.....yet... Problem?
        if self.using_branches:
            raise Exception('Age relations cannot be determined from BRANCH data.')
        if self.uniframe is None:
            print(f'Multiple_distribution fields: {dir(self)}')
            raise Exception('Multiple distribution object doesnt contain unified frame.')
        else:
            uniframe = self.uniframe

        if big_plot:

            plot_loc_counter = 0
            plotting_df = pd.DataFrame(columns=['code', 'r', 'c', 'ax', 'intersectframe', 'col_start'
                , 'col_end'])
            plotting_set_counts = {}
            for _, row in uniframe.iterrows():
                code = row.code
                nodeframe = row.uni_nd.nodeframe
                traceframe = row.uni_ld.lineframe_main
                traceframe['startpoint'] = traceframe.geometry.apply(tools.line_start_point)
                traceframe['endpoint'] = traceframe.geometry.apply(tools.line_end_point)
                traceframe = traceframe.reset_index(drop=True)
                xypointsframe = tools.get_xy_points_frame_from_frame(nodeframe)
                sets = traceframe.set.loc[traceframe['set'] > -1].unique().tolist()
                sets.sort()
                set_counts = traceframe.groupby('set').count()
                plotting_set_counts[code] = set_counts
                if len(sets) < 2:
                    raise Exception('Only one set defined. Cannot determine XY relations')
                # COLOR CYCLE FOR BARS
                start = 0
                end = 2
                # START OF COMPARISONS
                for idx, s in enumerate(sets):
                    # If final set: Skip the final set, comparison already done.
                    if idx == len(sets) - 1:
                        break
                    compare_sets = sets[idx + 1:]

                    for jdx, c_s in enumerate(compare_sets):
                        bf = traceframe.loc[(traceframe['set'] == s) | (traceframe['set'] == c_s)]
                        # TODO: More stats in age_relations?
                        # bfs_count = len(traceframe.loc[(traceframe['set'] == s)])
                        # bfcs_count = len(traceframe.loc[(traceframe['set'] == c_s)])

                        mpf = tools.get_matching_points(xypointsframe, bf)

                        intersectframe = tools.get_intersect_frame(mpf, bf, (s, c_s))
                        intersectframe = intersectframe.groupby(['pointclass', 'setpair']).size()
                        intersectframe = intersectframe.unstack()

                        addition = {'code': code, 'plot_loc_counter': plot_loc_counter,
                                    'intersectframe': intersectframe, 'col_start': start, 'col_end': end}
                        plotting_df = plotting_df.append(addition, ignore_index=True)
                        # MOVE COLORS CYCLE
                        start += 2
                        end += 2
                        # MOVE PLOT LOC COUNTER
                        plot_loc_counter += 1

        self.xy_relations_frame, self.relations_set_counts = plotting_df, plotting_set_counts

    def plot_xy_age_relations_unified(self, save=False, savefolder=None):
        if self.using_branches:
            raise Exception('Age relations cannot be determined from BRANCH data.')
        rel_frame = self.xy_relations_frame
        style = templates.styled_text_dict
        box_prop = templates.styled_prop
        colors_cycle = templates.colors_for_xy_relations
        # SUBPLOTS, FIGURE SETUP
        plot_count = len(self.uniframe) * len(self.set_list)
        cols = len(self.set_list)
        if plot_count % cols == 0:
            rows = plot_count // cols
        else:
            rows = plot_count // cols + 1
        width = 18
        height = (width / cols) * (rows * 0.75)
        # fig = plt.figure(figsize=(width, height))
        # gs = plt.GridSpec(nrows=rows, ncols=cols+1, figure=fig)
        fig, axes = plt.subplots(ncols=cols, nrows=rows, figsize=(width, height))
        rel_frame['axe'] = None
        for idx, row in rel_frame.iterrows():
            intersectframe = row.intersectframe
            colors = colors_cycle[row.col_start:row.col_end]
            plot_loc_counter = row.plot_loc_counter
            code = row.code
            r = plot_loc_counter // cols
            c = plot_loc_counter % cols
            ax = axes[int(r)][int(c)]
            rel_frame.axe.iloc[idx] = ax
            try:
                ipb = intersectframe.plot.bar(title=None, ax=ax, legend=None
                                              , colors=colors, linewidth=1, edgecolor='k', zorder=5)
                ipb.patches = ipb.patches[1:]
                ipb.patches[1].xy = (-0.125, 0)
                ipb.patches[1].width = 2
                ipb.patches[1].linewidth = 5
            except TypeError:
                continue
            # TICK FORMATS
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
            labels = ax.get_yticklabels()
            for label in labels:
                label.set_fontsize(20)
                label.set_rotation(0)
            # plt.yticks(ax.get_yticks(), l, fontsize=20)
            # TITLES ON THE LEFT SIDE
            if c == 0:
                name = code
                ax.text(s=name, x=-0.55, y=0.5, transform=ax.transAxes
                        , fontdict=style, bbox=box_prop
                        , ha='center', va='center'
                        , multialignment='center', fontsize=27)
            # LINE COUNTS FOR SETS ON THE RIGHT SIDE TODO
            if c == cols - 1:
                count_text = 'SET\nTRACE COUNTS'
                set_counts = self.relations_set_counts[code]
                for idx_, row_ in set_counts.iterrows():
                    if idx_ == -1:
                        continue
                    count_text = count_text + '\nSET {}: {}'.format(idx_, row_.geometry)
                ax.text(s=count_text, x=1.45, y=0.5, transform=ax.transAxes
                        , bbox=box_prop
                        , ha='center', va='center'
                        , multialignment='center', fontsize=20)
            # TICK LABELS
            ax.set_xlabel('')
            plt.xticks()
            labels = ax.get_xticklabels()
            # l = []
            for label in labels:
                label.set_fontsize(22)
                label.set_fontweight('semibold')
                label.set_rotation(0)
                # l.append(label)
            # plt.xticks(ax.get_xticks(), l, fontsize=22)
            # XLABEL AT BOTTOM ONLY
            if r == len(axes) - 1:
                ax.set_xlabel('NODE CLASS', fontsize='28', style='italic')

        df = pd.DataFrame(columns=['handle', 'label'])
        for axe in axes:
            for ax in axe:
                handles, labels = ax.get_legend_handles_labels()
                for handle, label in zip(handles, labels):
                    df = df.append({'handle': handle, 'label': label}, ignore_index=True)

        df = df.drop_duplicates(subset='label')
        handles = df.handle.tolist()
        labels = df.label.tolist()
        # MULTIPLE LEGENDS
        leg_frame = rel_frame.loc[rel_frame.plot_loc_counter < cols]
        hl = []
        for idx, s in enumerate(self.set_list):
            hand = handles[idx * 2:idx * 2 + 2]
            lab = labels[idx * 2:idx * 2 + 2]
            hl.append([hand, lab])
        legs = []
        for idx, row in leg_frame.iterrows():
            leg = row.axe.legend(hl[idx][0], hl[idx][1], loc=(0.3, 1.2), fontsize=20)
            legs.append(leg)
        for legenda in legs:
            fig.add_artist(legenda)
        # fig.legend(handles, labels, loc='center right', fontsize=20, borderaxespad=1)
        plt.subplots_adjust(right=0.8, left=0.2)
        if save:
            savename = Path(savefolder + '/xy_relations_all.png')
            plt.savefig(savename, dpi=200)

    def determine_xy_relations_all(self):
        # Determines xy relations and dynamically creates a dataframe as an aid for plotting the relations
        # TODO: No within set relations.....yet... Problem?
        if self.using_branches:
            raise Exception('Age relations cannot be determined from BRANCH data.')

        plot_loc_counter = 0
        plotting_df = pd.DataFrame(columns=['code', 'r', 'c', 'ax', 'intersectframe', 'col_start'
            , 'col_end'])
        plotting_set_counts = {}
        for _, row in self.df.iterrows():
            code = row.TargetAreaLines.name_code
            nodeframe = row.TargetAreaNodes.nodeframe
            traceframe = row.TargetAreaLines.lineframe_main
            traceframe['startpoint'] = traceframe.geometry.apply(tools.line_start_point)
            traceframe['endpoint'] = traceframe.geometry.apply(tools.line_end_point)
            traceframe = traceframe.reset_index(drop=True)
            xypointsframe = tools.get_xy_points_frame_from_frame(nodeframe)
            sets = traceframe.set.loc[traceframe['set'] > -1].unique().tolist()
            sets.sort()
            set_counts = traceframe.groupby('set').count()
            plotting_set_counts[code] = set_counts
            if len(sets) < 2:
                raise Exception('Only one set defined. Cannot determine XY relations')
            # COLOR CYCLE FOR BARS
            start = 0
            end = 2
            # START OF COMPARISONS
            for idx, s in enumerate(sets):
                # If final set: Skip the final set, comparison already done.
                if idx == len(sets) - 1:
                    break
                compare_sets = sets[idx + 1:]

                for jdx, c_s in enumerate(compare_sets):
                    bf = traceframe.loc[(traceframe['set'] == s) | (traceframe['set'] == c_s)]
                    # TODO: More stats in age_relations?
                    # bfs_count = len(traceframe.loc[(traceframe['set'] == s)])
                    # bfcs_count = len(traceframe.loc[(traceframe['set'] == c_s)])

                    mpf = tools.get_matching_points(xypointsframe, bf)

                    intersectframe = tools.get_intersect_frame(mpf, bf, (s, c_s))
                    intersectframe = intersectframe.groupby(['pointclass', 'setpair']).size()
                    intersectframe = intersectframe.unstack()

                    addition = {'code': code, 'plot_loc_counter': plot_loc_counter,
                                'intersectframe': intersectframe, 'col_start': start, 'col_end': end}
                    plotting_df = plotting_df.append(addition, ignore_index=True)
                    # MOVE COLORS CYCLE
                    start += 2
                    end += 2
                    # MOVE PLOT LOC COUNTER
                    plot_loc_counter += 1

        self.xy_relations_frame_indiv, self.relations_set_counts_indiv = plotting_df, plotting_set_counts

    def plot_xy_age_relations_all(self, save=False, savefolder=None):
        if self.using_branches:
            raise Exception('Age relations cannot be determined from BRANCH data.')
        rel_frame = self.xy_relations_frame_indiv
        style = templates.styled_text_dict
        box_prop = templates.styled_prop
        colors_cycle = templates.colors_for_xy_relations
        # SUBPLOTS, FIGURE SETUP
        plot_count = len(self.df) * len(self.set_list)
        cols = len(self.set_list)
        if plot_count % cols == 0:
            rows = plot_count // cols
        else:
            rows = plot_count // cols + 1
        width = 16
        height = (width / cols) * (rows * 0.75)

        # BIG PLOT
        fig, axes = plt.subplots(ncols=cols, nrows=rows, figsize=(width, height), sharex='col')
        rel_frame['axe'] = None
        # START PLOTTING AXES
        for idx, row in rel_frame.iterrows():
            intersectframe = row.intersectframe
            colors = colors_cycle[row.col_start:row.col_end]
            plot_loc_counter = row.plot_loc_counter
            code = row.code
            r = plot_loc_counter // cols
            c = plot_loc_counter % cols
            ax = axes[int(r)][int(c)]
            rel_frame.axe.iloc[idx] = ax
            try:
                ipb = intersectframe.plot.bar(title=None, ax=ax, legend=None
                                              , colors=colors, linewidth=1, edgecolor='k', zorder=5)
            except TypeError:
                continue
            # TICK FORMATS
            ax.yaxis.set_major_formatter(FormatStrFormatter('%.0f'))
            # TITLES ON THE LEFT SIDE
            if c == 0:
                name = code
                ax.text(s=name, x=-0.36, y=0.5, transform=ax.transAxes
                        , fontdict=style, bbox=box_prop
                        , ha='center', va='center'
                        , multialignment='center', fontsize=18)
            # LINE COUNTS FOR SETS ON THE RIGHT SIDE TODO
            if c == cols - 1:
                count_text = 'SET\nTRACE COUNTS'
                set_counts = self.relations_set_counts_indiv[code]
                for idx_, row_ in set_counts.iterrows():
                    if idx_ == -1:
                        continue
                    count_text = count_text + '\nSET {}: {}'.format(idx, row_.geometry)
                ax.text(s=count_text, x=1.28, y=0.5, transform=ax.transAxes
                        , bbox=box_prop
                        , ha='center', va='center'
                        , multialignment='center', fontsize=13)
            # TICK LABELS AT BOTTOM
            if r == len(axes) - 1:
                labels = ax.get_xticklabels()
                labs = []
                for label in labels:
                    label.set_fontsize(19)
                    label.set_fontweight('semibold')
                    label.set_rotation(0)
                    labs.append(label)
                plt.xticks(ax.get_xticks(), labs)

                ax.set_xlabel('NODE CLASS', fontsize='22', style='italic')

        df = pd.DataFrame(columns=['handle', 'label'])
        for axe in axes:
            for ax in axe:
                handles, labels = ax.get_legend_handles_labels()
                for handle, label in zip(handles, labels):
                    df = df.append({'handle': handle, 'label': label}, ignore_index=True)
        df = df.drop_duplicates(subset='label')
        handles = df.handle.tolist()
        labels = df.label.tolist()
        # MULTIPLE LEGENDS
        leg_frame = rel_frame.loc[rel_frame.plot_loc_counter < cols]
        hl = []
        for idx, s in enumerate(self.set_list):
            hand = handles[idx * 2:idx * 2 + 2]
            labs = labels[idx * 2:idx * 2 + 2]
            hl.append([hand, labs])
        legs = []
        for idx, row in leg_frame.iterrows():
            leg = row.axe.legend(hl[idx][0], hl[idx][1], loc=(0.3, 1.2), fontsize=20)
            legs.append(leg)
        for legenda in legs:
            fig.add_artist(legenda)
        # fig.legend(handles, labels, loc='center right', fontsize=20, borderaxespad=1)
        plt.subplots_adjust(right=0.85, left=0.15)
        if save:
            savename = Path(savefolder + '/xy_relations_indiv_all.png')
            plt.savefig(savename, dpi=200)

    def plot_all_xyi(self, save=False, savefolder=None):
        # MAKE INDIVIDUAL PLOTS
        for idx, row in self.df.iterrows():
            nd = row['TargetAreaNodes']
            nd.plot_xyi(save=save, savefolder=savefolder)

    def plot_all_xyi_unified(self, save=False, savefolder=None):
        for idx, row in self.uniframe.iterrows():
            fig = plt.figure()
            nd = row['uni_nd']
            nd.plot_xyi(save=save, savefolder=savefolder)

        fig, ax = plt.subplots(figsize=(8, 8))
        scale = 100

        fig, tax = ternary.figure(ax=ax, scale=scale)
        tools.initialize_ternary_points(ax, tax)
        for idx, row in self.uniframe.iterrows():
            nd = row['uni_nd']
            nd.plot_xyi_point(tax=tax)
        tools.tern_plot_the_fing_lines(tax)
        tax.legend(loc=(-0.10, 0.85), fontsize=20,
                   prop={'family': 'Times New Roman', 'weight': 'heavy'})

        fig.subplots_adjust(top=0.8)
        if save:
            savename = Path(savefolder + '/all_xyi_points.png')
            plt.savefig(savename, dpi=150)

    def plot_all_branch_ternary_unified(self, save=False, savefolder=None):
        if not self.using_branches:
            raise Exception('Branch classifications cannot be determined from traces.')
        fig, ax = plt.subplots(figsize=(8, 8))
        scale = 100
        fig, tax = ternary.figure(ax=ax, scale=scale)
        tools.initialize_ternary_branches_points(ax, tax)
        for idx, row in self.uniframe.iterrows():
            ld = row['uni_ld']
            ld.plot_branch_ternary_point(tax=tax)
        tools.tern_plot_branch_lines(tax)
        tax.legend(loc=(-0.10, 0.85), fontsize=11,
                   prop={'family': 'Times New Roman', 'weight': 'heavy'})
        plt.subplots_adjust(top=0.8)
        if save:
            savename = Path(savefolder + '/all_branch_points.png')
            plt.savefig(savename, dpi=150)

    def plot_all_branch_ternary(self, save=False, savefolder=None):
        if not self.using_branches:
            raise Exception('Branch classifications cannot be determined from traces.')

        scale = 100
        for idx, row in self.df.iterrows():
            fig, ax = plt.subplots(figsize=(8, 8))
            fig, tax = ternary.figure(ax=ax, scale=scale)
            tools.initialize_ternary_branches_points(ax, tax)
            ld = row['TargetAreaLines']
            ld.plot_branch_ternary_point(tax=tax)
            # COUNTS
            text = 'Amount of branches: ' + str(len(ld.lineframe_main)) \
                   + '\nC - C count: ' + str(len(ld.lineframe_main.loc[ld.lineframe_main.Connection == 'C - C'])) \
                   + '\nC - I count: ' + str(len(ld.lineframe_main.loc[ld.lineframe_main.Connection == 'C - I'])) \
                   + '\nI - I count: ' + str(len(ld.lineframe_main.loc[ld.lineframe_main.Connection == 'I - I']))

            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.65, 1.05, text, transform=ax.transAxes, fontsize=18, weight='roman', verticalalignment='top',
                    bbox=props,
                    fontfamily='Times New Roman')
            ax.legend(loc=(-0.15, 0.9), fontsize=25, prop={'family': 'Times New Roman', 'weight': 'heavy', 'size': 20})

            if save:
                savename = Path(savefolder + '/{}_branch_class.png'.format(ld.name_code))
                plt.savefig(savename, dpi=150)

    def gather_topology_parameters_unified(self):
        branches = self.using_branches
        self.uniframe['topology'] = None
        topology_appends = []
        for idx, row in self.uniframe.iterrows():
            code = row.code
            ld = row.uni_ld
            nd = row.uni_nd
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
                topology_dict = {'code': code,
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
                topology_dict = {'code': code,
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
            self.uniframe.topology[idx] = topoframe
        self.uniframe_topology_concat = pd.concat(self.uniframe.topology.tolist(), ignore_index=True)

    def plot_topology_unified(self, save=False, savefolder=None):
        branches = self.using_branches
        log_scale_columns = ['Mean Length', 'Areal Frequency B20',
                             'Fracture Intensity B21', 'Fracture Intensity P21', 'Areal Frequency P20']
        prop = templates.styled_prop
        units_for_columns = templates.units_for_columns
        topology_concat = self.uniframe_topology_concat
        topology_concat['color'] = topology_concat.code.apply(tools.find_color_topology_plot)
        topology_concat['order'] = topology_concat.code.apply(tools.find_order_topology_plot)
        topology_concat = topology_concat.sort_values(by='order', axis=0)
        if branches:
            columns_to_plot = ['Mean Length', 'Connections per Branch',
                               'Areal Frequency B20', 'Fracture Intensity B21',
                               'Dimensionless Intensity B22']
        else:
            columns_to_plot = ['Mean Length', 'Connections per Trace',
                               'Areal Frequency P20', 'Fracture Intensity P21',
                               'Dimensionless Intensity P22']

        for column in columns_to_plot:
            fig, ax = plt.subplots(figsize=(9, 9))
            topology_concat.code = topology_concat.code.astype('category')
            topology_concat.plot.bar(x='code', y=column,
                                     zorder=5, alpha=0.9, width=0.6, ax=ax, label='error')
            # PLOT STYLING
            ax.set_xlabel('')
            ax.set_ylabel(column + ' ' + f'({units_for_columns[column]})', fontsize=28, fontfamily='Times New Roman'
                          , style='italic')
            ax.set_title(x=0.5, y=1.1, label=column, fontsize=29,
                         bbox=prop, transform=ax.transAxes)
            legend = ax.legend()
            legend.remove()
            if column in log_scale_columns:
                ax.set_yscale('log')
            fig.subplots_adjust(top=0.85, bottom=0.35, left=0.2, right=0.95, hspace=0.2, wspace=0.2)
            locs, labels = plt.xticks()
            plt.yticks(fontsize=28, c='black')
            for label in labels:
                label._text = label._text.replace('_', '\n')
            plt.xticks(locs, labels, fontsize=28, c='black')
            # MOD xTICKS
            # CHANGE LEGEND HANDLES WITHOUT CHANGEING PLOT
            # for t in xticks:
            #     lh._sizes = [30]

            # VALUES IN BARS
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
                        ha='center', va='bottom', zorder=10, fontsize=25)

            if save:
                savename = Path(savefolder + '/{}_all.png'.format(str(column)))
                plt.savefig(savename, dpi=150)

    def plot_hexbin_plot(self, save=False, savefolder=None):
        branches = self.using_branches
        lf = self.uniframe_lineframe_main_concat
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
        # Main ax texts
        ax_main.text(x=0.75, y=0.33, s='LiDAR Data', transform=ax_main.transAxes, rotation=-50, fontsize=20)
        ax_main.text(x=0.29, y=0.60, s='Drone Data', transform=ax_main.transAxes, rotation=-50, fontsize=20)
        # Bottom ax texts
        ax_bottom.text(x=0.66, y=0.63, s='LiDAR Data', transform=ax_bottom.transAxes, fontsize=20)
        ax_bottom.text(x=0.22, y=0.63, s='Drone Data', transform=ax_bottom.transAxes, fontsize=20)
        # Title
        if branches:
            fig.suptitle('Comparison of LiDAR and UAV line counts\nBranches', fontsize=26)
        else:
            fig.suptitle('Comparison of LiDAR and UAV line counts\nTraces', fontsize=26)
        # Colorbar
        cb = fig.colorbar(hb, cax=ax_right)
        cb.set_label('Line Count Colorbar', fontsize=26)
        # Saving the figure
        if save:
            if branches:
                savename = Path(savefolder + '/hexbinplot_branches_with_histo.png')
            else:
                savename = Path(savefolder + '/hexbinplot_traces_with_histo.png')
            plt.savefig(savename, dpi=200)

    def plot_anisotropy_unified(self, ellipse_weights=False, save=False, savefolder=None):
        if not self.using_branches:
            raise Exception('Anisotropy cannot be determined from traces.')
        for idx, row in self.uniframe.iterrows():
            row.uni_ld.calc_anisotropy(ellipse_weights=ellipse_weights)
            row.uni_ld.plot_anisotropy_styled()
            style = templates.styled_text_dict
            prop = templates.styled_prop
            plt.title(row.code, loc='left', fontdict=style, fontsize=25, bbox=prop)
            if save:
                savename = Path(savefolder + '/{}_anisotropy_unified.png'.format(row.code))
                plt.savefig(savename, dpi=200)

    def plot_anisotropy_all(self, ellipse_weights=False, save=False, savefolder=None):
        for idx, row in self.df.iterrows():
            row.TargetAreaLines.calc_anisotropy(ellipse_weights=ellipse_weights)
            row.TargetAreaLines.plot_anisotropy_styled()
            plt.title(row.TargetAreaLines.name_code, loc='left')
            if save:
                savename = Path(savefolder + '/{}_anisotropy.png'.format(row.TargetAreaLines.name_code))
                plt.savefig(savename, dpi=200)


class MultiTargetAreaQGIS(MultiTargetArea):
    # TODO: Implement cut-offs into input: list => table
    # TODO: Implement sets
    def __init__(self, table_df, group_names, branches, debug_logger, cut_offs=False):
        self.debug_logger = debug_logger
        self.cut_offs = cut_offs
        # TODO: Swtich from codes to groups
        self.groups = group_names
        self.codes = group_names
        self.table_df = table_df

        self.using_branches = branches
        # TODO: Remove filename when isn't used
        self.df = pd.DataFrame(columns=['name', 'lineframe', 'areaframe', 'nodeframe', 'group', 'cut_off', 'filename'])

        # Assign None to later initialized attributes
        # TODO: TEST PROPERLY
        self.set_list = None
        self.uniframe = None
        self.uniframe_lineframe_main_concat = None
        self.uni_left, self.uni_right, self.uni_top, self.uni_bottom = None, None, None, None
        self.relations_set_counts = None
        self.xy_relations_frame = None
        self.xy_relations_frame_indiv = None
        self.relations_set_counts = None
        self.uniframe_topology_concat = None
        self.relations_set_counts_indiv = None

        for idx, row in table_df.iterrows():
            name = row.Name
            if self.using_branches:
                lineframe = row.Branch_frame
            else:
                lineframe = row.Trace_frame
            areaframe = row.Area_frame
            nodeframe = row.Node_frame
            group = row.Group
            if not self.cut_offs:
                cut_off = 1
            else:
                # TODO: Implement cut-offs
                cut_off = 1
            # Initialize DataFrames with additional columns
            lineframe['azimu'] = lineframe.geometry.apply(tools.calc_azimu)
            lineframe['halved'] = lineframe.azimu.apply(tools.azimu_half)
            nodeframe['c'] = nodeframe.Class.apply(str)

            # Change MultiLineStrings to LineStrings. Delete unmergeable MultiLineStrings. A trace should be mergeable.
            if isinstance(lineframe.geometry.iloc[0], shapely.geometry.MultiLineString):
                debug_logger.write_to_log_time(f'before linemerge:\n {lineframe.geometry}')
                non_mergeable_idx = []
                for idx, row in lineframe.iterrows():
                    try:
                        lineframe.geometry.iloc[idx] = shapely.ops.linemerge(row.geometry)
                    except ValueError:
                        debug_logger.write_to_log_time(f'non-mergeable, ValueError:\n {lineframe.geometry.iloc[idx]}')
                        non_mergeable_idx.append(idx)
                    # Should be LineString if mergeable. If not:
                    if isinstance(lineframe.geometry.iloc[idx], shapely.geometry.MultiLineString):
                        debug_logger.write_to_log_time(f'non-mergeable, is MLS:\n {lineframe.geometry.iloc[idx]}')
                        non_mergeable_idx.append(idx)
                # Drop non-mergeable
                lineframe = lineframe.drop(index=non_mergeable_idx)

                debug_logger.write_to_log_time(f'after linemerge:\n {lineframe.geometry}')

            if self.using_branches:
                lineframe['c'] = lineframe.Class.apply(str)
                lineframe['connection'] = lineframe.Connection.apply(str)

            # Append to DataFrame
            self.df = self.df.append({'name': name, 'lineframe':lineframe, 'areaframe':areaframe
                                         , 'nodeframe':nodeframe, 'group':group, 'cut_off':cut_off, 'filename': 'DEBUG'}, ignore_index=True)

        self.norm_list = tools.get_area_normalisations_frames(self.df.areaframe.tolist())
        norm_array = np.asarray(self.norm_list)
        self.df['norm'] = norm_array
        self.df['TargetAreaLines'] = self.df.apply(
            lambda x: tools.construct_length_distribution_base(x['lineframe'], x['areaframe'], x['name'],
                                                               x['cut_off'],
                                                               x['norm'], x['filename'], self.using_branches),
            axis=1)
        self.df['TargetAreaNodes'] = self.df.apply(
            lambda x: tools.construct_node_data_base(x['nodeframe'], x['group'], x['name']), axis=1)

    def unified(self):
        self.debug_logger.write_to_log_time(f'\ndf before unified:\n {self.df}')
        uniframe = pd.DataFrame(columns=['uni_ld', 'uni_nd', 'group', 'uni_ld_area', 'uni_rep_circles_area'])
        for idx, group in enumerate(self.groups):
            # TODO: This code shit should be (fixed), now to implement!
            # frame_debug = self.df.loc[self.df['code'].str.contains(code)]
            # # Code should represent part before a '_' symbol

            self.debug_logger.write_to_log_time(f'group for frame{group}')
            frame = self.df.loc[self.df['group'] == group]
            self.debug_logger.write_to_log_time(f'frame from group{frame.head()}')
            # frame = self.df.loc[self.df['group'].str.contains(group)]

            # if not frame.equals(frame_debug):  # DEBUGGING
            #     print(code, frame.head(), frame_debug.head())  # DEBUGGING
            #     raise Exception('Given code doesnt represent the part before a "_" symbol. CHECK GIVEN CODES!')
            # det_frame = frame.loc[frame['code'].str.contains('_det')]
            # m20_frame = frame.loc[frame['code'].str.contains('_20m')]
            # lidar_frame = frame.loc[frame['code'].str.contains('_LiDAR')]
            if len(frame) > 0:
                unif_ld_main = tools.unify_lds(frame.TargetAreaLines.tolist(), group)
                unif_ld_main.calc_attributes()
                uni_ld_area = gpd.GeoDataFrame(pd.concat(frame.areaframe.tolist(), ignore_index=True))
                unif_nd_main = tools.unify_nds(frame.TargetAreaNodes.tolist())
                uniframe = uniframe.append(
                    {'uni_ld': unif_ld_main, 'uni_nd': unif_nd_main, 'code': group, 'uni_ld_area': uni_ld_area},
                    ignore_index=True)
            else:
                self.debug_logger.write_to_log_time(f'code: {self.groups}')
                self.debug_logger.write_to_log_time(f'code: {group}')
                self.debug_logger.write_to_log_time('Group Name didnt match frames.. len(frame) == 0')
                raise Exception('len(frame) == 0')
            # if len(det_frame) > 0:
            #     temp_code = code + '_det'
            #     unif_ld_main = tools.unify_lds(det_frame.TargetAreaLines.tolist())
            #     unif_ld_main.calc_attributes()
            #     uni_ld_area = gpd.GeoDataFrame(pd.concat(det_frame.areaframe.tolist(), ignore_index=True))
            #     unif_nd_main = tools.unify_nds(det_frame.TargetAreaNodes.tolist())
            #     uniframe = uniframe.append(
            #         {'uni_ld': unif_ld_main, 'uni_nd': unif_nd_main, 'code': temp_code, 'uni_ld_area': uni_ld_area},
            #         ignore_index=True)
            # if len(m20_frame) > 0:
            #     temp_code = code + '_20m'
            #     unif_ld_main = tools.unify_lds(m20_frame.TargetAreaLines.tolist())
            #     unif_ld_main.calc_attributes()
            #     uni_ld_area = gpd.GeoDataFrame(pd.concat(m20_frame.areaframe.tolist(), ignore_index=True))
            #     unif_nd_main = tools.unify_nds(m20_frame.TargetAreaNodes.tolist())
            #     uniframe = uniframe.append(
            #         {'uni_ld': unif_ld_main, 'uni_nd': unif_nd_main, 'code': temp_code, 'uni_ld_area': uni_ld_area},
            #         ignore_index=True)
            # if len(lidar_frame) > 0:
            #     temp_code = code + '_LiDAR'
            #     unif_ld_main = tools.unify_lds(lidar_frame.TargetAreaLines.tolist())
            #     unif_ld_main.calc_attributes()
            #     uni_ld_area = gpd.GeoDataFrame(pd.concat(lidar_frame.areaframe.tolist(), ignore_index=True))
            #     unif_nd_main = tools.unify_nds(lidar_frame.TargetAreaNodes.tolist())
            #     uniframe = uniframe.append(
            #         {'uni_ld': unif_ld_main, 'uni_nd': unif_nd_main, 'code': temp_code, 'uni_ld_area': uni_ld_area},
            #         ignore_index=True)

        uniframe = tools.norm_unified(uniframe)
        self.uniframe = uniframe
        # AIDS FOR PLOTTING:
        self.uniframe_lineframe_main_concat = pd.concat([srs.lineframe_main for srs in self.uniframe.uni_ld], sort=True)
        self.uni_left, self.uni_right = tools.calc_xlims(self.uniframe_lineframe_main_concat)
        self.uni_top, self.uni_bottom = tools.calc_ylims(self.uniframe_lineframe_main_concat)

        self.debug_logger.write_to_log_time(f'\nuniframe after unified:\n {self.uniframe}')


