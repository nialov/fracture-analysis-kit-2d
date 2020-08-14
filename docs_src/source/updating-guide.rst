**Updating Guide**
======================

This page contains the guide for updating the plugin. Updating consists of firstly removing
the plugin from QGIS and then installing it again.

.. _updating_warning:

Warning
--------------------------

If you wish to update the plugin with commits made to GitHub there is a chance that Python module
requirements have changed. This might require re-running the **updated** installation script.
If you encounter error messages demanding installation of new plugins during the Updating process,
see :doc:`installation`
and re-run the installation script as documented there **after downloading the new .zip file**.

Updating
--------

* Download the new plugin .zip file from `GitHub <https://github.com/nialov/fracture-analysis-kit-2d>`_
* Open QGIS and uninstall the current plugin installation:

  * *Plugins* -> *Manage and Install Plugins...* -> *Installed* -> *2D Fracture Analysis Kit*
    -> *Uninstall Plugin* -> *Yes*
* Restart QGIS (Close and open up again)
* Now to install the updated plugin:

  * *Plugins* -> *Manage and Install Plugins...* -> *Install from ZIP* -> *...*
    -> Choose the downloaded .zip file -> *Install Plugin* -> *Yes*
  * If an error message pop-ups demanding installation of additional Python modules,
    see :ref:`updating_warning`

Plugin updated, congratulations!
