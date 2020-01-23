import matplotlib as plt
import matplotlib.patheffects as path_effects
import numpy as np

# Bounding box with wheat color
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)


def styling_plots(style):
    # plt.style.use('default')
    plt.rc('font', size=13, family='Times New Roman')
    if style == 'traces':
        plt.rc('axes', facecolor='seashell', linewidth=0.75, grid=True)
    if style == 'branches':
        plt.rc('axes', facecolor='#CDFFE6', linewidth=0.75, grid=True)
    if style == 'gray':
        plt.rc('axes', facecolor='lightgrey', linewidth=0.75, grid=True)
    plt.rc('grid', linewidth=0.75, c='k', alpha=0.5)
    plt.rc('legend', facecolor='wheat', shadow=True, framealpha=1, edgecolor='k')
    plt.rc('scatter', marker='+')
    plt.rc('figure', edgecolor='k', frameon=True, figsize=(8, 6))
    plt.rc('xtick', bottom=True)
    plt.rc('ytick', left=True)
    # plt.rc('lines', markersize=16)
    # plt.rc('path', effects=[path_effects.withStroke(linewidth=5, foreground='w')])
    # plt.rc('xlabel', {'alpha':1})


styled_text_dict = {'path_effects': [path_effects.withStroke(linewidth=3, foreground='k')]
    , 'c': 'w'}

styled_prop = dict(boxstyle='round', pad=0.6, facecolor='wheat',
                   path_effects=[path_effects.SimplePatchShadow(), path_effects.Normal()])
# TODO: This is stupid
color_dict = dict(KB_det='coral', KB_20m='teal', KL_det='brown', KL_20m='blue', OG_det='khaki', OG_20m='darkkhaki',
                  Hastholmen_LiDAR='grey', Loviisa_LiDAR='black', OG5_det='coral', OG4_0_20m='teal', OG4_1_20m='blue',
                  OG4_2_20m='darkkhaki', OG4_3_20m='grey', OG4_4_20m='black')

color_dict_code = dict(KB='teal', KL='blue', OG='darkkhaki', Hastholmen='grey', Loviisa='black'
                       , OG5='coral', OG4_0='teal', OG4_1='blue', OG4_2='darkkhaki', OG4_3='grey', OG4_4='black')

detailed = ['KB4', 'KB8', 'KL3', 'KL4', 'OG2', 'OG5']

# area_ellipses = {'KB2': [(466359.59, 6691318.0), 45, 12, 0]
#                  , 'KB3': [(466534.64, 6691406.52), 90, 14, -50]
#                  , 'KB7': [(466021.6, 6692119.24), 23, 10, -64]
#                  , 'KB9': [(466051.69, 6691966.09), 14, 5, -45]
#                  , 'KB10': [(466105.0, 6691907.19), 40, 13, -50]
#                  , 'KB11': [(466022.74, 6691584.14), 26, 16, -46]
#                  , 'KL2_1': [(468241.37, 6689918.8), 24, 8, -63]
#                  , 'KL2_2': [(468397.79, 6689778.34), 140, 20, -40]
#                  , 'KL5': [(468881.24, 6689160.21), 32, 11, -21]
#                  , 'KB4': [(466582.46, 6691353.7), 14, 10, -90]
#                  , 'KB8': [(466011.42, 6692130.02), 9, 5, -80]
#                  , 'KL3': [(468309.13, 6689859.61), 24, 7, -49]
#                  , 'KL4': [(468337.36, 6689830.72), 13, 5, -80]
#                  , 'Loviisa': [(491335.11, 6719824.0), 50000, 50000, 0]
#                  , 'Hastholmen': [(469053.12, 6692981.51), 5000, 5000, 0]}

# SET 0 blue, SET 1 red, set 2 green
colors_for_xy_relations = ['blue', 'red', 'lightblue', 'green', 'orangered', 'greenyellow']

angles_for_examination = np.arange(0, 179, 30)

columns_to_plot_branches = {'Mean Length', 'Connections per Branch',
                            'Areal Frequency B20', 'Fracture Intensity B21',
                            'Dimensionless Intensity B22'}

columns_to_plot_traces = {'Mean Length', 'Connections per Trace',
                          'Areal Frequency P20', 'Fracture Intensity P21',
                          'Dimensionless Intensity P22'}

units_for_columns = {'Mean Length': 'm', 'Connections per Branch': '1/n',
                     'Areal Frequency B20': '1/m^2', 'Fracture Intensity B21': 'm/m^2',
                     'Dimensionless Intensity P22': 'm^2/m^2', 'Connections per Trace': '1/n',
                     'Areal Frequency P20': '1/m^2', 'Fracture Intensity P21': 'm/m^2',
                     'Dimensionless Intensity B22': '-'}
