# -*- coding: utf-8 -*-
"""
/***************************************************************************
 FractureAnalysis2D
                                 A QGIS plugin
 Analysis of lineament & fracture traces, branches and nodes
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2020-01-12
        copyright            : (C) 2020 by Nikolas Ovaskainen
        email                : nikolasovaskainen@hotmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""
# import sys, os

#Add kit directory to python path TODO: Fix
# currentPath = os.path.dirname( __file__ )
# sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/fracture_analysis_kit'))

# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load FractureAnalysis2D class from file FractureAnalysis2D.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .fracture_analysis_2d import FractureAnalysis2D
    return FractureAnalysis2D(iface)
