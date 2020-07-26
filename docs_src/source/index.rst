.. Fracture Analysis 2D documentation master file, created by
   sphinx-quickstart on Sat Feb 15 14:33:49 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

**Fracture Analysis 2D**
================================================

.. toctree::
   :maxdepth: 2




Description
-----------
This QGIS plugin can be used to extract lineament & fracture size, abundance and topological parameters
from two-dimensional GIS polylines along with their topological branches and nodes.
The results will be given as graphical plots.

The plugin is **experimental** and installation requires the **manual installation** of a few external python libraries.

This plugin uses four types of vector data as inputs:
*traces* (Polylines), *branches* (Polylines), *nodes* (Points) and *areas* (Polygons).

*Traces* can be manually or automatically digitized GIS polyline features from e.g.
Light Detection And Ranging (LiDAR) digital elevation models (DEMs)
or from drone orthophotography of bedrock outcrop surfaces.
*Branches* and *nodes* are derived from :ref:`ngt`.
*Areas* are the interpretation boundaries of the traces and branches.


Example plots
-------------

.. image:: imgs/collage1.png
	:scale: 25 %
	:align: center



.. _installation:

**Installation**
==================

The plugin is **experimental** and installation requires the **manual installation** of a few external Python libraries.
Installation requirements and guide below.

.. toctree::
   :maxdepth: 2

   installation

Legacy Installation
===================

**WARNING**

**This is the legacy installation method without the complementary installation script. Usage entirely at your
own risk. Updates to this guide are not guaranteed when Python dependencies change.**

.. toctree::
   :maxdepth: 2

   legacy-installation

**Usage Help**
==================


**Dependencies and References**
===============================

References
----------

Both branches and nodes are derived from :ref:`ngt`.
For their definition along with the definition of the plots and the plotted parameters,
I refer you to multiple sources. Sources are in order of importance.

* `Nyberg et al., 2018 <https://pubs.geoscienceworld.org/gsa/geosphere/article/531129/networkgt-a-gis-tool-for-geometric-and-topological>`_

	* *NetworkGT Plugin introduction and guide.*

* `Sanderson and Nixon, 2015 <https://www.sciencedirect.com/science/article/pii/S0191814115000152>`_

	* *Trace and branch size, abundance and topological parameter definitions.*

* My Master's Thesis, Ovaskainen, 2020

	* *Plots used in my Thesis were done with an older version of the same code used for this plugin.*

* `Sanderson and Peacock, 2020 <https://www.sciencedirect.com/science/article/abs/pii/S001282521930594X>`_

	* *Information about rose plots.*
* `Bonnet et al., 2001 <https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/1999RG000074>`_

	* *Length distribution modelling.*

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

.. _external_Python_modules:

External Python modules
-----------------------
This plugin is dependant on external Python libraries (and their subsequent dependancies) that are not installed by default in QGIS.

* GDAL_
* Fiona_
* geopandas_
* Python-ternary_
* sklearn_
* seaborn_
* powerlaw_

See :ref:`installation` for installation guide.

.. _geopandas: https://geopandas.org/
.. _Python-ternary: https://github.com/marcharper/Python-ternary
.. _GDAL: https://gdal.org/
.. _Fiona: https://fiona.readthedocs.io/en/latest/
.. _sklearn: https://scikit-learn.org/stable/index.html
.. _seaborn: https://seaborn.pydata.org/index.html
.. _powerlaw: https://github.com/jeffalstott/powerlaw

**Doc**
==================

For Developers: Plugin documentation
------------------------------------

This plugin has been developed in PyCharm by setting the Python environment to mimic the OSGeo4W Shell.
Good guide `here <http://spatialgalaxy.net/2018/02/13/quick-guide-to-getting-started-with-pyqgis-3-on-windows/>`_.

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



