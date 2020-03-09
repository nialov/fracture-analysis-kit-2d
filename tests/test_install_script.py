import hypothesis
from hypothesis.strategies import floats, text, lists
from hypothesis import given, settings
import shapely
from shapely.geometry import Point, LineString, Polygon

import numpy as np
import pandas as pd
import geopandas as gpd
import ternary
import config
import install_script


class TestInstallScript:

    def test_check_installations(self):
        install_script.check_installations()

    def test_is_gdal_needed(self):
        result = install_script.is_gdal_needed()
        assert result is False

    def test_is_installation_needed(self):
        result = install_script.is_installation_needed()
        assert result is False

    def test_verify_external_downloads(self):
        try:
            install_script.verify_external_downloads(True, True)
        except FileNotFoundError:
            pass
