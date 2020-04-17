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
from fracture_analysis_kit import tools \
    , multiple_target_areas \
    , analysis_and_plotting \
    , qgis_tools


class TestTools:
    line_float = floats(-1, 1)
    coord_strat_1 = lists(line_float, min_size=2, max_size=2)
    coord_strat_2 = lists(line_float, min_size=2, max_size=2)

    halved_strategy = floats(0, 180)
    length_strategy = floats(0)

    @given(coord_strat_1, coord_strat_2)
    @settings(max_examples=5)
    def test_calc_azimu(self, coords_1, coords_2):
        simple_line = LineString([coords_1, coords_2])
        tools.calc_azimu(simple_line)
        ass = tools.calc_azimu(LineString([(0, 0), (1, 1)]))
        assert np.isclose(ass, 45.)

    def test_azimuth_plot_attributes(self):
        res = tools.azimuth_plot_attributes(
            pd.DataFrame({'azimu': np.array([0, 45, 90]), 'length': np.array([1, 2, 1])}))
        assert np.allclose(res, np.array([33.33333333, 0., 0., 0., 0.,
                                          33.33333333, 0., 0., 0., 33.33333333,
                                          0., 0., 0., 0., 0.,
                                          0., 0., 0., 33.33333333, 0.,
                                          0., 0., 0., 33.33333333, 0.,
                                          0., 0., 33.33333333, 0., 0.,
                                          0., 0., 0., 0., 0.,
                                          0.]))

    def test_tern_plot_the_fing_lines(self):
        _, tax = ternary.figure()
        tools.tern_plot_the_fing_lines(tax)

    def test_tern_plot_branch_lines(self):
        _, tax = ternary.figure()
        tools.tern_plot_branch_lines(tax)

    def test_aniso_get_class_as_value(self):
        classes = ('C - C', 'C - I', 'I - I')
        assert tools.aniso_get_class_as_value(classes[0]) == 1
        assert tools.aniso_get_class_as_value(classes[2]) == 0
        assert tools.aniso_get_class_as_value("asd") == 0

    @given(halved_strategy, length_strategy)
    @settings(max_examples=10)
    def test_aniso_calc_anisotropy_1(self, halved, length):
        c = "C - C"
        result = tools.aniso_calc_anisotropy(halved, c, length)
        for val in result:
            assert val >= 0

    def test_aniso_calc_anisotropy_2(self):
        result = tools.aniso_calc_anisotropy(90, 'C - C', 10)
        assert np.allclose(result, np.array([
            6.12323400e-16,
            5.00000000e+00,
            8.66025404e+00,
            1.00000000e+01,
            8.66025404e+00,
            5.00000000e+00]))
        result_0 = tools.aniso_calc_anisotropy(90, 'C - I', 10)
        assert np.allclose(result_0, np.array([0, 0, 0, 0, 0, 0]))

    def test_calc_y_distribution(self):
        df = pd.DataFrame({"length": [1, 2, 3, 4, 5, 6, 2.5]})
        area = 10
        result_df = tools.calc_y_distribution(df, area)
        result_df = result_df.reset_index()
        assert np.isclose(result_df.y.iloc[-1], 7 / 10)
        assert result_df.length.max() == result_df.length.iloc[0]

    def test_calc_cut_off_length(self):
        result = tools.calc_cut_off_length(pd.DataFrame({'length': np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])}), 0.55)
        assert np.isclose(result, 4.5)

    def test_define_set(self):
        result_1 = tools.define_set(50, pd.DataFrame({'Set': [1, 2], 'SetLimits': [(10, 90), (100, 170)]}))
        assert result_1 == '1'
        result_2 = tools.define_set(99, pd.DataFrame({'Set': [1, 2], 'SetLimits': [(10, 90), (100, 170)]}))
        assert result_2 == '-1'

    @given(coord_strat_1, coord_strat_2)
    @settings(max_examples=10)
    def test_line_end_point(self, coords1, coords2):
        line = LineString([coords1, coords2])
        tools.line_start_point(line)

    def test_get_nodes_intersecting_sets(self):
        p = gpd.GeoDataFrame(data={'geometry': [Point(0, 0), Point(1, 1), Point(3, 3)]})
        l = gpd.GeoDataFrame(
            data={'geometry': [LineString([(0, 0), (2, 2)]), LineString([(0, 0), (0.5, 0.5)])], 'set': [1, 2]})

        result = tools.get_nodes_intersecting_sets(p, l)
        assert isinstance(result, gpd.GeoDataFrame)
        assert result.geometry.iloc[0] == Point(0.00000, 0.00000)

    def test_get_intersect_frame(self):
        nodes = gpd.GeoDataFrame({'geometry': [Point(0, 0), Point(1, 1)], 'c': ['Y', 'X']})
        traces = gpd.GeoDataFrame(data={'geometry': [
            LineString([(-1, -1), (2, 2)]), LineString([(0, 0), (-0.5, 0.5)]), LineString([(2, 0), (0, 2)])]
            , 'set': [1, 2, 2]})
        traces['startpoint'] = traces.geometry.apply(tools.line_start_point)
        traces['endpoint'] = traces.geometry.apply(tools.line_end_point)
        sets = (1, 2)
        intersect_frame = tools.get_intersect_frame(nodes, traces, sets)
        assert intersect_frame.node.iloc[0] == Point(0, 0)
        assert intersect_frame.sets.iloc[0] == (2, 1)


class TestMultipleTargetAreas:

    # noinspection PyPep8Naming
    def test_MultiTargetAreaQGIS(self, tmp_path):
        # noinspection PyTypeChecker
        class Dummy(analysis_and_plotting.MultiTargetAreaAnalysis):

            # noinspection PyMissingConstructor
            def __init__(self):
                return

        dummy = Dummy()
        layer_table_df = pd.DataFrame(
            columns=['Name', 'Group', 'Branch_frame', 'Trace_frame', 'Area_frame', 'Node_frame'])
        line_1 = LineString([(0, 0), (0.5, 0.5)])
        line_2 = LineString([(0, 0), (0.5, -0.5)])
        line_3 = LineString([(0, 0), (1, 0)])
        branch_frame = gpd.GeoDataFrame({"geometry": [line_1, line_2, line_3]
                                            , "Connection": ["C - C", "C - I", "I - I"]
                                            , "Class": ["X - I", "Y - Y", "I - I"]})

        trace_frame = gpd.GeoDataFrame({"geometry": [line_1, line_2]})
        point_1 = Point(0.5, 0.5)
        point_2 = Point(1, 1)
        point_3 = Point(10, 10)
        node_frame = gpd.GeoDataFrame({"geometry": [point_1, point_2, point_3], "Class": ["X", "Y", "I"]})
        area_1 = Polygon([(0, 0), (1, 1), (1, 0)])
        area_frame = gpd.GeoDataFrame({"geometry": [area_1]})
        name = "test1"
        group = "T1"

        set_df = pd.DataFrame({'Set': [1, 2], 'SetLimits': [(40, 50), (130, 140)]})

        table_append = {'Name': name
            , 'Group': group
            , 'Branch_frame': branch_frame
            , 'Trace_frame': trace_frame
            , 'Area_frame': area_frame
            , 'Node_frame': node_frame}

        layer_table_df = layer_table_df.append(table_append, ignore_index=True)

        group_names_cutoffs_df = pd.DataFrame({'Group': [group], 'CutOffTraces': [0], 'CutOffBranches': [0]})

        dummy.determine_relationships = False
        dummy.layer_table_df = layer_table_df
        dummy.group_names_cutoffs_df = group_names_cutoffs_df
        dummy.set_df = set_df

        dummy.analysis()

        config.g_list = ["T1"]
        config.ta_list = ["test1"]
        config.n_g = 1
        config.n_ta = 1

        plotting_directory = qgis_tools.plotting_directories(str(tmp_path), "TEST")
        dummy.plotting_directory = plotting_directory
        dummy.plot_results()