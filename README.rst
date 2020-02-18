

**Fracture Analysis 2D**
================================================


This QGIS plugin can be used to extract lineament & fracture size, abundance and topological parameters 
from two-dimensional GIS polylines along with their topological branches and nodes. 
The results will be given as graphical plots.

The plugin is **experimental** and installation requires the **manual installation** of a few external python libraries. 

This plugin uses three types of vector data as inputs: *traces*, *branches* and *nodes*. 
Traces can be manually or automatically digitized GIS polyline features from e.g. 
Light Detection And Ranging (LiDAR) digital elevation models (DEMs)
or from drone orthophotography of bedrock outcrop surfaces. 

.. image:: images/collage1.png
	:scale: 25 %
	:align: center
	

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