**Installation Guide**
======================

Requirements and warnings
--------------------------

This plugin has **only** been tested on Windows. No functionality on other platforms guaranteed and
the installation will be different than the one explained below.

Installation requires external Python dependencies that need to be installed to the QGIS OSGeo
environment.
This might cause issues and errors that I cannot predict especially when another module with
external Python dependencies is installed in the same environment.
**The entire risk as to the quality and performance of this plugin and its installation is with you.**

Installation using the installation script
------------------------------------------

Info
~~~~

This plugin comes packed with a Python installation script that will install the plugin's required
Python dependencies.
Also packed with the script are unofficial Windows Binaries for Python packages *fiona* and *GDAL*.

These are from https://www.lfd.uci.edu/~gohlke/pythonlibs/

Download plugin .zip and install it
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* To start, download the plugin .zip file from: https://github.com/nialov/fracture-analysis-kit-2d

  * Scroll down on GitHub for instructions (**Plugin Download**).

* Next, open QGIS and install the plugin.

  * In QGIS go to *Plugins* -> *Manage and Install Plugins...* -> *Install from ZIP*
  * Select the downloaded .zip file -> *Install Plugin*
  * This installation will most likely fail due to the lack of external Python dependencies,
    don't worry about this. Installation of these is covered next.

Running installation script in the OSGeo4WShell
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

* Now to install external Python dependencies the complementary installation script is used.
  The installation script must be run from a command shell that is connected to the
  QGIS Python environment. The shell is named *OSGeo4WShell*.
  Installing Python dependencies in the QGIS environment is done using the *OSGeo4WShell*.

  * Easiest way to find the Shell is to:

    * Press Windows key to open start menu
    * Type: *OSGeo4WShell*
    * The executable should show up, just start it up.

      * However, if you believe you have other tools connected that might have their own
        OSGeo4WShell associated with them, you might consider checking the location associated
        with the windows shortcut (Right click shortcut -> *Open file location* -> Right click the
        next shortcut -> *Open file location*). The location should either be in OSGeo4W64 or QGIS
        directories.

  * The *OSGeo4WShell* can also be located by finding your QGIS installations. There it is named
    *OSGeo4W.bat*:

    * Example locations:

      * C:\OSGeo4W64
      * C:\Program Files\QGIS

* First run a command in the OSGeo4WShell::

    py3_env

  * As the name suggests, this will initialize OSGeo4WShell to use Python 3 instead of Python 2.

* The OSGeo4WShell prompt must now be changed to the same directory where the plugin was installed by QGIS

  * Typical location::

        C:\Users\your-username-here\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\fracture_analysis_2d

  * The plugin directory can also be located by trying to install the plugin, the directory is printed out
    in the error message when installation fails.

  * To change directory, type in the shell with **your plugin installation path** after the *cd*::

        cd C:\Users\your-username-here\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\fracture_analysis_2d

* Now the hard part is over and the installation script can be run to install Python dependencies.
  Type in the OSGeo4WShell::

    python install_script.py

* Installation errors will be printed out if encountered.

Finalization
~~~~~~~~~~~~

* If all went well with the dependency installation now the plugin can be fully installed.

  * Go back to QGIS and install the plugin from the .zip for the final time.

    * *Plugins* -> *Manage and Install Plugins...* -> *Install from ZIP* -> *...*
      -> Choose the downloaded .zip file -> *Install Plugin* -> *Yes*

  * The installation should succeed without any pop-up errors or warnings.

* Installation complete!

