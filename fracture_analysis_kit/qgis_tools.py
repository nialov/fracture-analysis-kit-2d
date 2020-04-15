"""
Contains tools relevant to QGIS layer transformations and plugin functionality.
"""

import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
from qgis.PyQt.QtWidgets import QMessageBox
from qgis.core import QgsMessageLog, Qgis


# Convert QGIS vectorlayer to pandas DataFrame
def layer_to_df(layer):
    """
    Converts QGIS vector layer to a pandas DataFrame and extracts coordinate system from the layer.

    :param layer: QGIS vector layer.
    :type layer: qgis.core.QgsVectorLayer
    :return: Converted pandas DataFrame and layer coord system.
    :rtypes: pandas.DataFrame & qgis.core.QgsCoordinateReferenceSystem
    """
    fieldnames = [field.name() for field in layer.fields()]
    fieldnames.append('geometry')
    features = layer.getFeatures()
    coord_system = layer.crs()
    df = pd.DataFrame(columns=fieldnames)
    for feature in features:
        row_add = {}
        for fn in fieldnames:
            if 'geometry' in fn:
                row_add[fn] = feature.geometry()
            else:
                row_add[fn] = feature[fn]
            # print(row_add[fn])
        # print(row_add)
        df = df.append(row_add, ignore_index=True)
    # for fn in fieldnames:
    #     column_features = [feat[fn] for feat in features]
    #     appendage = {fn: column_features}
    #     df = df.append(appendage, ignore_index=True)
    # DEBUGGING LOG

    return df, coord_system


def df_to_gdf(df, coord_system):
    """
    Converts pandas DataFrame to a GeoDataFrame along with setting the given coordinate system.

    :param df: Pandas DataFrame with QGIS vector layer data.
    :type df: pandas.DataFrame
    :param coord_system: Given coordinate system.
    :type coord_system: qgis.core.QgsCoordinateReferenceSystem
    :return: Converted GeoDataFrame
    :rtype: geopandas.GeoDataFrame
    """
    proj_rep = coord_system.toProj()
    gdf = gpd.GeoDataFrame(df)
    gdf.crs = proj_rep
    return gdf


def layer_to_gdf(layer):
    """
    Converts QGIS vector layer to a GeoDataFrame.

    :param layer: QGIS vector layer
    :type layer: qgis.core.QgsVectorLayer
    :return: Converted GeoDataFrame
    :rtype: geopandas.GeoDataFrame
    """
    df, coord_system = layer_to_df(layer)
    return df_to_gdf(df, coord_system)


def plotting_directories(results_folder, name):
    """
    Creates plotting directories and handles FileExistsErrors when raised.

    :param results_folder: Base folder to create plots_{name} folder to.
    :type results_folder: str
    :param name: Analysis name.
    :type name: str
    :return: Newly made path to plotting directory where all plots will be saved to.
    :rtype: str
    """
    plotting_directory = f"{results_folder}/plots_{name}"
    try:
        try:
            os.mkdir(Path(plotting_directory))
        except FileExistsError:
            print("Earlier plots exist. Overwriting old ones.")
            return
        os.mkdir(Path(f"{plotting_directory}/age_relations"))
        os.mkdir(Path(f"{plotting_directory}/age_relations/indiv"))
        os.mkdir(Path(f"{plotting_directory}/anisotropy"))
        os.mkdir(Path(f"{plotting_directory}/anisotropy/indiv"))
        os.mkdir(Path(f"{plotting_directory}/azimuths"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/indiv"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/equal_radius"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/equal_radius/traces"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/equal_radius/branches"))

        os.mkdir(Path(f"{plotting_directory}/azimuths/equal_area"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/equal_area/traces"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/equal_area/branches"))

        os.mkdir(Path(f"{plotting_directory}/azimuths/indiv/equal_radius"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/indiv/equal_radius/traces"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/indiv/equal_radius/branches"))

        os.mkdir(Path(f"{plotting_directory}/azimuths/indiv/equal_area"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/indiv/equal_area/traces"))
        os.mkdir(Path(f"{plotting_directory}/azimuths/indiv/equal_area/branches"))

        os.mkdir(Path(f"{plotting_directory}/branch_class"))
        os.mkdir(Path(f"{plotting_directory}/branch_class/indiv"))
        os.mkdir(Path(f"{plotting_directory}/length_distributions"))
        os.mkdir(Path(f"{plotting_directory}/length_distributions/branches"
                      )
                 )
        os.mkdir(Path(f"{plotting_directory}/length_distributions/branches/predictions")
                 )
        os.mkdir(Path(f"{plotting_directory}/length_distributions/traces"))
        os.mkdir(Path(f"{plotting_directory}/length_distributions/traces/predictions"))
        os.mkdir(Path(f"{plotting_directory}/length_distributions/indiv"))
        os.mkdir(Path(f"{plotting_directory}/length_distributions/indiv/branches"))
        os.mkdir(Path(f"{plotting_directory}/length_distributions/indiv/traces"))
        os.mkdir(Path(f"{plotting_directory}/topology"))
        os.mkdir(Path(f"{plotting_directory}/topology/branches"))
        os.mkdir(Path(f"{plotting_directory}/topology/traces"))
        os.mkdir(Path(f"{plotting_directory}/xyi"))
        os.mkdir(Path(f"{plotting_directory}/xyi/indiv"))
        os.mkdir(Path(f"{plotting_directory}/hexbinplots"))

    # Should not be needed (shutil.rmtree(Path(f"{plotting_directory}"))).
    # Would run if only SOME of the above folders are present.
    # i.e. Folder creation has failed and same folder is used again or if some folders have been removed and same
    # plotting directory is used again. Edge cases.
    except FileExistsError:
        QMessageBox.critical(title="Error",
                             text=f'Given folder contains a plots_{name} -folder with incomplete folders.\n'
                                  f'Try again with new folder and analysis name.')
        raise
        # print("Earlier decrepit directories found. Deleting decrepit result-plots folder in plots and remaking.")
        # shutil.rmtree(Path(f"{plotting_directory}"))

    return plotting_directory
