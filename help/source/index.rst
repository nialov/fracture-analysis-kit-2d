.. Fracture Analysis 2D documentation master file, created by
   sphinx-quickstart on Sat Feb 15 14:33:49 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**Fracture Analysis 2D**
================================================

Description
-----------
This QGIS plugin can be used to extract lineament & fracture size, abundance and topological parameters 
from two-dimensional GIS polylines along with their topological branches and nodes. 
The results will be given as graphical plots.

The plugin is **experimental** and installation requires the **manual installation** of a few external python libraries. 
Installation requirements and guide below.

This plugin uses three types of vector data as inputs: *traces*, *branches* and *nodes*. 
Traces can be manually or automatically digitized GIS polyline features from e.g. 
Light Detection And Ranging (LiDAR) digital elevation models (DEMs)
or from drone orthophotography of bedrock outcrop surfaces. 
The plugin doesn't discriminate between traces extracted using different datasets.

Both branches and nodes are derived from :ref:`ngt`. 
For their definition along with the definition of the plots and the plotted parameters, 
I refer you to multiple sources. Sources are in order of importance.

* Nyberg et al., 2018

	* NetworkGT Plugin introduction and guide.
* Sanderson and Nixon, 2015

	* Trace and branch size, abundance and topological parameter definitions.
* My Master's Thesis, Ovaskainen, 2020

	* Plots used in my Thesis were done with an older version of the same code used for this plugin.
* Sanderson and Peacock, 2020

	* Information about rose plots.
* Bonnet et al., 2001

	* Length distribution modelling.


Example plots
-------------

*Cross-cutting and abutting relationships between sets.*

.. image:: imgs/KB_20m_crosscutting_abutting_relationships.png
	:scale: 25 %
	:alt: alternate text
	:align: center

*Equal-area length-weighted rose plot of fracture branches.*

.. image:: imgs/KB_20m_group_weighted_azimuths.png
	:scale: 25 %
	:alt: alternate text
	:align: center

*Length distributions of lineament & fracture branches along with numerically fitted power-law trendline.*

.. image:: imgs/UNIFIED_CUT_LD_WITH_FIT.png
	:scale: 25 %
	:alt: alternate text
	:align: center
   
.. _installation:

**Installation**
==================

Requirements
------------

Plugin has **only** been tested on Windows. No functionality on other platforms guaranteed.

External Python module installation
-----------------------------------


**Help**
==================



**Dependencies and References**
===============================

.. _ngt:

NetworkGT
-------------

This plugin has been built to **only** work with data extracted using another QGIS-plugin, NetworkGT_ (see: `Nyberg et al., 2018`__):

	*The NetworkGT (Network Geometry and Topology) Toolbox is a set of tools designed for 
	the geometric and topological analysis of fracture networks.*

If the input data (*traces*) you have can be processed in NetworkGT into *branches* and *nodes* 
it is suitable for this plugin. NetworkGT is available for both QGIS and ArcGIS
and branch and node data from both *should* be valid inputs into this plugin (*as of 15.2.2020*).


.. _NetworkGT: https://github.com/BjornNyberg/NetworkGT
.. _Nyberg2018: https://pubs.geoscienceworld.org/gsa/geosphere/article/531129/networkgt-a-gis-tool-for-geometric-and-topological
__ Nyberg2018_

.. _external_python_modules:

External Python modules
-----------------------
This plugin is dependant on external Python libraries (and their subsequent dependancies) that are not installed by default in QGIS. 

* geopandas_
* python-ternary_
* todo

See :ref:`installation` for installation guide.

.. _geopandas: https://geopandas.org/
.. _python-ternary: https://github.com/marcharper/python-ternary


**Doc**
==================

For Developers: Plugin documentation
------------------------------------

Documentation for Python modules has been created using Autodoc. Autodoc has trouble running without setting the matplotlib backend to Qt5Agg. 
If you wish to remake documentation: Check conf.py and replace my 'QT_QPA_PLATFORM_PLUGIN_PATH' with your own path.

.. toctree::
   :maxdepth: 4
   
   fracture_analysis_2d


**Indices and tables**
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`



