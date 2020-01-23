from pathlib import Path

import dill
import os
import shutil

import kit_resources.multiple_target_areas as mta
import kit_resources.templates as templates


def analyze_data(
    analysis_name,
    branchdirs,
    tracedirs,
    nodedirs,
    areadirs,
    codes,
    cut_offs_branches,
    cut_offs_traces,
    set_list,
):
    # Create instances for both traces and branches
    trace_data = mta.MultiTargetArea(
        tracedirs, areadirs, nodedirs, codes, cut_offs_traces, branches=False
    )
    branch_data = mta.MultiTargetArea(
        branchdirs, areadirs, nodedirs, codes, cut_offs_branches, branches=True
    )

    # BRANCH DATA SETUP
    branch_data.calc_attributes_for_all()
    branch_data.define_sets_for_all(set_list)

    branch_data.unified()

    branch_data.create_setframes_for_all_unified()
    branch_data.gather_topology_parameters_unified()

    # TRACE DATA SETUP
    trace_data.calc_attributes_for_all()
    trace_data.define_sets_for_all(set_list)
    trace_data.calc_curviness_for_all()

    trace_data.unified()

    trace_data.create_setframes_for_all_unified()
    trace_data.determine_xy_relations_all()
    trace_data.determine_xy_relations_unified()
    trace_data.gather_topology_parameters_unified()

    # Use dill to store calculated data
    with Path("calc_data/dill_{}_branch_data.pkl".format(analysis_name)).open(
        mode="w+b"
    ) as file:
        dill.dump(branch_data, file)
    with Path("calc_data/dill_{}_trace_data.pkl".format(analysis_name)).open(
        mode="w+b"
    ) as file:
        dill.dump(trace_data, file)

    # dill.dump(trace_data, Path('calc_data/dill_{}_trace_data'.format(analysis_name)))


def plot_data(analysis_name, predict_with):
    def plotting_directories(analysis_name):
        try:
            try:
                os.mkdir(Path("plots/plots_{}".format(analysis_name)))
            except FileExistsError:
                print("Earlier plots exist. Overwriting old ones.")
                return
            os.mkdir(Path("plots/plots_{}/age_relations".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/age_relations/indiv".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/anisotropy".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/azimuths".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/azimuths/traces".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/azimuths/branches".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/branch_class".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/length_distributions".format(analysis_name)))
            os.mkdir(
                Path(
                    "plots/plots_{}/length_distributions/branches".format(analysis_name)
                )
            )
            os.mkdir(
                Path(
                    "plots/plots_{}/length_distributions/branches/predictions".format(
                        analysis_name
                    )
                )
            )
            os.mkdir(
                Path("plots/plots_{}/length_distributions/traces".format(analysis_name))
            )
            os.mkdir(
                Path(
                    "plots/plots_{}/length_distributions/traces/predictions".format(
                        analysis_name
                    )
                )
            )
            os.mkdir(
                Path("plots/plots_{}/length_distributions/indiv".format(analysis_name))
            )
            os.mkdir(
                Path(
                    "plots/plots_{}/length_distributions/indiv/branches".format(
                        analysis_name
                    )
                )
            )
            os.mkdir(
                Path(
                    "plots/plots_{}/length_distributions/indiv/traces".format(
                        analysis_name
                    )
                )
            )
            os.mkdir(Path("plots/plots_{}/topology".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/topology/branches".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/topology/traces".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/xyi".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/xyi/individual".format(analysis_name)))
            os.mkdir(Path("plots/plots_{}/hexbinplots".format(analysis_name)))

        # Should not be needed. Will run if only SOME of the above folders are present.
        except FileExistsError:
            print(
                "Earlier decrepit directories found. Deleting decrepit result-plots folder in plots and remaking."
            )
            shutil.rmtree(Path("plots/plots_{}".format(analysis_name)))

    # Savefolder initialization
    plotting_directories(analysis_name)

    # Open calculated data files
    with Path("calc_data/dill_{}_branch_data.pkl".format(analysis_name)).open(
        mode="rb"
    ) as file:
        branch_data = dill.load(file)
    with Path("calc_data/dill_{}_trace_data.pkl".format(analysis_name)).open(
        mode="rb"
    ) as file:
        trace_data = dill.load(file)

    savefolder_base = "plots/plots_{}".format(analysis_name)

    # ___________________BRANCH DATA_______________________
    templates.styling_plots("branches")

    # branch_data.plot_lengths_all(save=True, savefolder=savefolder_base + '/length_distributions/indiv/branches')
    # branch_data.plot_lengths_unified()
    # branch_data.plot_lengths_unified_combined(save=True, savefolder=savefolder_base + '/length_distributions/branches')

    # Length distribution predictions
    # for p in predict_with:
    #     branch_data.plot_lengths_unified_combined_predictions(
    #         save=True, savefolder=savefolder_base + '/length_distributions/branches/predictions', predict_with=p)
    # TODO: Fix azimuths plotting (redundant ellipse weighting)
    # branch_data.plot_all_azimuths(big_plots=True, save=True
    #                               , savefolder=savefolder_base + '/azimuths/branches')
    # branch_data.plot_unified_azimuths(big_plots=True, save=True
    #                                   , savefolder=savefolder_base + '/azimuths/branches')
    branch_data.plot_all_xyi(save=True, savefolder=savefolder_base + "/xyi/individual")
    # branch_data.plot_all_xyi_unified(save=True, savefolder=savefolder_base + '/xyi')
    # branch_data.plot_topology_unified(save=True, savefolder=savefolder_base + '/topology/branches')
    # branch_data.plot_hexbin_plot(save=True, savefolder=savefolder_base + '/hexbinplots')

    # ----------------unique for branches-------------------
    branch_data.plot_all_branch_ternary(
        save=True, savefolder=savefolder_base + "/branch_class"
    )
    branch_data.plot_all_branch_ternary_unified(
        save=True, savefolder=savefolder_base + "/branch_class"
    )
    # branch_data.plot_anisotropy_all(save=True, savefolder=savefolder_base + '/anisotropy')
    # branch_data.plot_anisotropy_unified(save=True, savefolder=savefolder_base + '/anisotropy')
    #
    # __________________TRACE DATA______________________
    # templates.styling_plots('traces')
    #
    # trace_data.plot_lengths_all(save=True, savefolder=savefolder_base + '/length_distributions/indiv/traces')
    # trace_data.plot_lengths_unified()
    # trace_data.plot_lengths_unified_combined(save=True, savefolder=savefolder_base + '/length_distributions/traces')
    #
    # Length distribution predictions
    # for p in predict_with:
    #     trace_data.plot_lengths_unified_combined_predictions(
    #         save=True, savefolder=savefolder_base + '/length_distributions/traces/predictions', predict_with=p)
    #
    # trace_data.plot_all_azimuths(big_plots=True, save=True
    #                              , savefolder=savefolder_base + '/azimuths/traces')
    # trace_data.plot_unified_azimuths(big_plots=True, save=True
    #                                  , savefolder=savefolder_base + '/azimuths/traces')
    # trace_data.plot_topology_unified(save=True, savefolder=savefolder_base + '/topology/traces')
    # trace_data.plot_hexbin_plot(save=True, savefolder=savefolder_base + '/hexbinplots')
    #
    # ---------------unique for traces-------------------
    # trace_data.plot_xy_age_relations_all(save=True, savefolder=savefolder_base + '/age_relations/indiv')
    # trace_data.plot_xy_age_relations_unified(save=True, savefolder=savefolder_base + '/age_relations')
    #
    # TODO: big plot for violins + legend?
    # trace_data.plot_curviness_for_unified(violins=True, save=True, savefolder=savefolder_base + '/curviness/traces')


#
