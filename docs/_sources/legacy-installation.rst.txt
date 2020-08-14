**Legacy Installation Guide**
=============================

Requirements and warnings
-------------------------

This plugin has **only** been tested on Windows. No functionality on other platforms guaranteed and
the installation will be different than the one explained below.

Installation requires external Python dependencies that need to be installed to the QGIS environment.
This might cause issues and errors that I cannot predict especially when another module with
external Python dependencies is installed.
**The entire risk as to the quality and performance is with you.**

**WARNING**

**This is the legacy installation method without the complementary installation script. Usage entirely at your
own risk. Updates to this guide are not guaranteed when Python dependencies change.**

Last updated: 26.7.2020

External Python module installation with administrator access
-------------------------------------------------------------

**WARNING**

**This is the legacy installation method without the complementary installation script. Usage entirely at your
own risk. Updates to this guide are not guaranteed when Python dependencies change.**

Last updated: 26.7.2020
First we will install *GDAL* and *Fiona*. Due to QGIS functionalities this cannot be done automatically through pip and instead we need to download the modules ourselves.
Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/
and find the files listed below.

You must download the right version depending on your operating system (32x OR 64x):

* GDAL

	* *GDAL-3.0.4-cp37-cp37m-win_amd64.whl (64-bit OS)*
	* **OR**
	* *GDAL-3.0.4-cp37-cp37m-win32.whl (32-bit OS)*

* Fiona

	* *Fiona-1.8.13-cp37-cp37m-win_amd64.whl (64-bit OS)*
	* **OR**
	* *Fiona-1.8.13-cp37-cp37m-win32.whl (32-bit OS)*


Next up: Start up OSGeo4W Shell as **administrator** (**Important!**).

This should pop up by searching in Windows start up menu.
(Press windows key on your keyboard and type "OSGeo4W Shell").

First, the OSGeo4w Shell must run a py3_env.bat file that is located in "Your QGIS installation folder path"\bin.

So, to get there, you must type or copy in the OSGeo4W Shell::

	cd /D "Your QGIS installation folder path without the quotes"\\bin

Next up, run the py3_env.bat file by typing in the Shell::

	py3_env

To install the just downloaded files the OSGeo4W Shell must be in the same directory as the downloaded files.
Go to where your *GDAL-..-.whl* and *Fiona-...-.whl* files are and copy the url
(Example URL: *F:\\Users\\nikke\\Downloads*).

We'll change the OSGeo4W Shell location by typing or copying into the Shell:

::

	cd /D "paste your url here without the quotes"

| The *GDAL* and *Fiona* installation depends on which version of both you downloaded.
| **If you have the 64x bit version, type or copy these into the OSGeo4W Shell**
| *Note: Install the GDAL file first.*

::

	python -m pip install GDAL-3.0.4-cp37-cp37m-win_amd64.whl

Press Enter and when installation is completed, type or copy::

	python -m pip install Fiona-1.8.13-cp37-cp37m-win_amd64.whl

**Else if you have the 32x bit versions, use these**::

	python -m pip install GDAL-3.0.4-cp37-cp37m-win32.whl

Press Enter and when installation is completed, type or copy in to the Shell::

	python -m pip install Fiona-1.8.13-cp37-cp37m-win32.whl

Hopefully the installation succeeds without issues. Next up we will install *geopandas*.
Type in the OSGeo4W Shell::

	python -m pip install geopandas

Next, we will install *python-ternary*. Type in the OSGeo4W Shell::

	python -m pip install python-ternary

Next, we will install *sklearn*. Type in the OSGeo4W Shell::

	python -m pip install sklearn

Next, we will install *seaborn*. Type in the OSGeo4W Shell::

	python -m pip install seaborn

Next, we will install *powerlaw*. Type in the OSGeo4W Shell::

	python -m pip install powerlaw

**And we are done! Installing the plugin itself is easy.**

External Python module installation without administrator access
----------------------------------------------------------------
First we will install *GDAL* and *Fiona*. Due to QGIS functionalities this cannot be done automatically through pip and instead we need to download the modules ourselves.
Go to: https://www.lfd.uci.edu/~gohlke/pythonlibs/
and find the files listed below.
You must download the right version depending on your operating system (32x OR 64x):

* GDAL

	* *GDAL-3.0.4-cp37-cp37m-win_amd64.whl (64-bit OS)*
	* **OR**
	* *GDAL-3.0.4-cp37-cp37m-win32.whl (32-bit OS)*

* Fiona

	* *Fiona-1.8.13-cp37-cp37m-win_amd64.whl (64-bit OS)*
	* **OR**
	* *Fiona-1.8.13-cp37-cp37m-win32.whl (32-bit OS)*


Next up: Start up OSGeo4W Shell.

This should pop up by searching for it in the Windows start up menu.
(Press windows key on your keyboard and just type "OSGeo4W Shell").

First, the OSGeo4w Shell must run a py3_env.bat file that is located in "Your QGIS installation folder path"\bin.
Sometimes the OSGeo4W Shell properly starts there and you can skip this part but if not:

You must type or copy in the OSGeo4W Shell::

	cd /D "Your QGIS installation folder path without the quotes"\bin

To install the just downloaded files the OSGeo4W Shell must be in the same directory as the downloaded files.
Go to where your *GDAL-..-.whl* and *Fiona-...-.whl* files are and copy the url
(Example URL: *F:\\Users\\nikke\\Downloads*).


We'll change the OSGeo4W Shell location by typing or copying into the Shell::

	cd /D "paste your url here without the quotes"

| The *GDAL* and *Fiona* installation depends on which version of both you downloaded.
| **If you have the 64x bit version, type or copy these into the OSGeo4W Shell**
| *Note: Install the GDAL file first.*

::

	python -m pip install GDAL-3.0.4-cp37-cp37m-win_amd64.whl --user

Press Enter and when installation is completed, type or copy::

	python -m pip install Fiona-1.8.13-cp37-cp37m-win_amd64.whl --user

**Else if you have the 32x bit versions, use these**::

	python -m pip install GDAL-3.0.4-cp37-cp37m-win32.whl --user

Press Enter and when installation is completed, type or copy in to the Shell::

	python -m pip install Fiona-1.8.13-cp37-cp37m-win32.whl --user

Hopefully the installation succeeds without issues. Next up we will install *geopandas*.
Type in the OSGeo4W Shell::

	python -m pip install geopandas --user

Next, we will install *python-ternary*. Type in the OSGeo4W Shell::

	python -m pip install python-ternary --user

Next, we will install *sklearn*. Type in the OSGeo4W Shell::

	python -m pip install sklearn --user

Next, we will install *seaborn*. Type in the OSGeo4W Shell::

	python -m pip install seaborn --user

Next, we will install *powerlaw*. Type in the OSGeo4W Shell::

	python -m pip install powerlaw --user

**And we are done! Installing the plugin itself is easy.**

Plugin installation from .zip file
-----------------------------------
After installing Python modules, you may install the plugin in QGIS.
Go to *Plugins* -> *Manage and Install Plugins...* and choose *Install from ZIP*.
Input the .zip file with the plugin and install (*fracture_analysis_2d.zip*).


