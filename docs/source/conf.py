# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))
sys.path.insert(0, os.path.abspath('../../..'))
sys.path.insert(0, os.path.abspath('../../fracture_analysis_kit'))


# -- Matplotlib backend setup ------------------------------------------------
# Required for sphinx to succesfully autodoc plugin modules.

import matplotlib
# IMPORTANT! Change this to your own path if remaking docs is required.
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'F:\Program Files\QGIS 3.10\apps\Qt5\plugins'
matplotlib.use('Qt5Agg')

# -- Project information -----------------------------------------------------

project = 'Fracture Analysis 2D'
copyright = '2020, Nikolas Ovaskainen'
author = 'Nikolas Ovaskainen'

# The full version, including alpha/beta/rc tags
release = '0.1alpha'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

doctest_test_doctest_blocks = 'yes'

# Mock QGIS imports
autodoc_mock_imports = ["qgis", "geopandas"]
