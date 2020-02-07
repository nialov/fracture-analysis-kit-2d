import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as patheffects

# Values used in spatial estimates of intersections
buffer_value = 0.001
snap_value = 0.001

# Lists information for plotting abundanze, size and topological parameters
columns_to_plot_branches = ['Mean Length', 'Connections per Branch',
                            'Areal Frequency B20', 'Fracture Intensity B21',
                            'Dimensionless Intensity B22']
columns_to_plot_traces = ['Mean Length', 'Connections per Trace',
                          'Areal Frequency P20', 'Fracture Intensity P21',
                          'Dimensionless Intensity P22']
units_for_columns = {'Mean Length': 'm', 'Connections per Branch': '1/n',
                     'Areal Frequency B20': '1/m^2', 'Fracture Intensity B21': 'm/m^2',
                     'Dimensionless Intensity P22': 'm^2/m^2', 'Connections per Trace': '1/n',
                     'Areal Frequency P20': '1/m^2', 'Fracture Intensity P21': 'm/m^2',
                     'Dimensionless Intensity B22': '-'}

# Angles used for anisotropy calculations
angles_for_examination = np.arange(0, 179, 30)

# Dictionary for styled text
styled_text_dict = {'path_effects': [patheffects.withStroke(linewidth=3, foreground='k')]
    , 'c': 'w'}

# Dictionary for a styled prop
styled_prop = dict(boxstyle='round', pad=0.6, facecolor='wheat',
                   path_effects=[patheffects.SimplePatchShadow(), patheffects.Normal()])

# Bounding box with wheat color
props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)

colors_for_xy_relations = ['blue', 'red', 'lightblue', 'green', 'orangered', 'greenyellow']

# TODO: Implement
color_dict = dict()

# Used for styling plots
def styling_plots(style):
    """
    Styles matplotlib plots by changing default matplotlib parameters.
    :param style: String to determine how to stylize. Options: 'traces', 'branches', 'gray'
    :type style: str
    """
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
