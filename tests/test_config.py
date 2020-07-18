"""
Tests for config.py file
"""

import config


class TestConfig:

    def test_get_color_dict(self):
        for unified in [True, False]:
            try:
                result = config.get_color_dict(unified=unified)
            except AssertionError:
                pass

        # Setup config stuff, then test
        # Number of target areas. Should be changed before analysis.
        config.n_ta = 4
        # Number of groups. Should be changed before analysis.
        config.n_g = 2
        # Target area name list
        config.ta_list = ["test_ta_1", "test_ta_2", "test_ta_3", "test_ta_4"]
        # Group name list
        config.g_list = ["test_g_1", "test_g_2"]

        for unified in [True, False]:
            result = config.get_color_dict(unified=unified)
            assert len(result) != 0

