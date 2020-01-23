import dill

import kit_resources.templates as templates

dill.load_session('dill_both_test.pkl')

# predict_with = ['KB_20m', 'KL_20m', 'Loviisa_LiDAR']
# predict_with = ['Hastholmen_LiDAR', 'Loviisa_LiDAR']


# ___________________BRANCH DATA_______________________
templates.styling_plots('branches')

# branch_data.plot_lengths_all(save=True, savefolder='plots/length_distributions/indiv/branches')
# branch_data.plot_lengths_unified()
# branch_data.plot_lengths_unified_combined(save=True, savefolder='plots/length_distributions/branches')
# branch_data.plot_lengths_unified_combined_predictions(save=True, savefolder='plots/length_distributions/branches/predictions', predict_with=['Hastholmen_LiDAR', 'Loviisa_LiDAR'])
# branch_data.plot_lengths_unified_combined_predictions(save=True, savefolder='plots/length_distributions/branches/predictions', predict_with=['KB_20m', 'KL_20m', 'Loviisa_LiDAR'])
# branch_data.plot_all_azimuths(ellipse_weights=True, big_plots=True, save=True
#                               , savefolder='plots/azimuths/branches')
# branch_data.plot_unified_azimuths(ellipse_weights=True, big_plots=True, save=True
#                               , savefolder='plots/azimuths/branches')
# branch_data.plot_all_xyi(save=True, savefolder='plots/xyi/individual')
# branch_data.plot_all_xyi_unified(save=True, savefolder='plots/xyi')
branch_data.plot_topology_unified(save=True, savefolder='plots/topology/branches')
# branch_data.plot_hexbin_plot(save=True, savefolder='plots/hexbinplots')


# ----------------unique for branches-------------------
# branch_data.plot_all_branch_ternary(save=True, savefolder='plots/branch_class')
# branch_data.plot_all_branch_ternary_unified(save=True, savefolder='plots/branch_class')
# branch_data.plot_anisotropy_all(save=True, savefolder='plots/anisotropy', ellipse_weights=False)
# branch_data.plot_anisotropy_unified(save=True, savefolder='plots/anisotropy', ellipse_weights=False)
#
# __________________TRACE DATA______________________
templates.styling_plots('traces')

# trace_data.plot_lengths_all(save=True, savefolder='plots/length_distributions/indiv/traces')
# trace_data.plot_lengths_unified()
# trace_data.plot_lengths_unified_combined(save=True, savefolder='plots/length_distributions/traces')
# trace_data.plot_lengths_unified_combined_predictions(save=True, savefolder='plots/length_distributions/traces/predictions', predict_with=['Hastholmen_LiDAR', 'Loviisa_LiDAR'])
# trace_data.plot_lengths_unified_combined_predictions(save=True, savefolder='plots/length_distributions/traces/predictions', predict_with=['KB_20m', 'KL_20m', 'Loviisa_LiDAR'])
# trace_data.plot_all_azimuths(ellipse_weights=True, big_plots=True, save=True
#                               , savefolder='plots/azimuths/traces')
# trace_data.plot_unified_azimuths(ellipse_weights=True, big_plots=True, save=True
#                               , savefolder='plots/azimuths/traces')
trace_data.plot_topology_unified(save=True, savefolder='plots/topology/traces')
# trace_data.plot_hexbin_plot(save=True, savefolder='plots/hexbinplots')

# ---------------unique for traces-------------------
# trace_data.plot_xy_age_relations_all(save=True, savefolder='plots/age_relations/indiv')
# trace_data.plot_xy_age_relations_unified(save=True, savefolder='plots/age_relations')


# TODO: big plot for violins + legend?
# trace_data.plot_curviness_for_unified(violins=True, save=True, savefolder='plots/curviness/traces')
