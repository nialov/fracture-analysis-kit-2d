**Fracture Analysis 2D**
================================================

.. toctree::
   :maxdepth: 2

Description
-----------
This QGIS plugin can be used to extract lineament & fracture size, abundance and topological parameters
from two-dimensional GIS polylines along with their topological branches and nodes.
The results will be given as graphical plots.

The plugin is **experimental** and installation requires the **installation** of a few external python libraries.
Installation is done using a Python script but requires some manual setup.

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

**Usage Guide**
==================

The plugin is controlled using a QGIS GUI interface. Guide below.

.. toctree::
   :maxdepth: 2

   usage

**Updating Guide**
==================

Contains guide for updating the plugin.

.. toctree::
   :maxdepth: 2

   updating-guide

**Dependencies and References**
===============================

References
----------

Both branches and nodes are derived from :ref:`ngt`.
For their definition along with the definition of the plots and the plotted parameters,
I refer you to multiple sources.

* `Nyberg et al., 2018 <https://pubs.geoscienceworld.org/gsa/geosphere/article/531129/networkgt-a-gis-tool-for-geometric-and-topological>`_

   * *NetworkGT Plugin introduction and guide.*
   * `NetworkGT GitHub <https://github.com/BjornNyberg/NetworkGT>`_

* `Sanderson and Nixon, 2015 <https://www.sciencedirect.com/science/article/pii/S0191814115000152>`_

   * *Trace and branch size, abundance and topological parameter definitions.*

* My Master's Thesis, Ovaskainen, 2020

   * *Plots used in my Thesis were done with an older version of the same code used for this plugin.*

* `Sanderson and Peacock, 2020 <https://www.sciencedirect.com/science/article/abs/pii/S001282521930594X>`_

   * *Information about rose plots.*

* `Alstott et al. 2014 <https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0085777>`_

   * *Length distribution modelling using the Python 3 powerlaw package.*
   * `powerlaw GitHub <https://github.com/jeffalstott/powerlaw>`_

* `Bonnet et al., 2001 <https://agupubs.onlinelibrary.wiley.com/doi/abs/10.1029/1999RG000074>`_

   * *Length distribution modelling.*

.. _ngt:

NetworkGT
~~~~~~~~~~

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

**Development**
=====================

This plugin has been developed in PyCharm by setting the Python environment to mimic the environment of OSGeo4W Shell.
Good guide for setup `here <http://spatialgalaxy.net/2018/02/13/quick-guide-to-getting-started-with-pyqgis-3-on-windows/>`_.

Documentation for Python modules has been created using `Autodoc <https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html>`_.
Autodoc has trouble running without setting the matplotlib backend to Qt5Agg.
If you wish to remake documentation: Check conf.py and replace my 'QT_QPA_PLATFORM_PLUGIN_PATH' with your own path.

The requirements_dev.txt file contains all pip packages (custom) installed within my QGIS environment.
It is therefore not *clean* and contains packages that are not required for development. It should contain
all **required** packages however when complemented with the QGIS environment Python 3 packages.

Tests
-----

To successfully run the plugin tests using pytest:

* Open ./tests/__init__.py
* Change to these Path variables to point to your QGIS installation::

   qt5_plugins = Path(r'F:\OSGeo4W64\apps\Qt5\plugins')
   qt5_path = Path(r'F:\OSGeo4W64\apps\Qt5')
   qgis_apps_path = Path(r'F:\OSGeo4W64\apps')

* Installation folder of QGIS differs based on whether you installed with:

  * **OSGeo4W Network Installer** or **QGIS Standalone Installer**
  * Standalone installation typically in *C:\\Program Files\\QGIS* or similar path

make.bat
---------

The make.bat file in the root directory runs with plain::

   make

* Tests using pytest
* Updates requirements_dev.txt for currently installer pip packages
* sphinx to build documentation

* For pb_tool to archive the plugin as an installable .zip file::

   make zip

  * Requires a zip installer (e.g. 7zip) on PATH

* To deploy the plugin to your QGIS plugin folder::

   make deploy

  * This is the primary source installation method. See: `pb_tool <http://g-sherman.github.io/plugin_build_tool/>`_
  * And check *./pb_tool.cfg* first


For Developers: Plugin documentation
------------------------------------

.. toctree::
   :maxdepth: 4

   fracture_analysis_2d


**Indices and tables**
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

