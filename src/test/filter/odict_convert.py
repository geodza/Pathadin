import unittest

from dataclasses import asdict

from slide_viewer.ui.model.filter.threshold_filter import ThresholdFilterData_, ManualThresholdFilterData, ThresholdType
from slide_viewer.ui.model.filter.base_filter import FilterData_, FilterType


class ODictConvertTest(unittest.TestCase):
    def test_manual_threshold_filter_data(self):
        d = ODict3({
            FilterData_.filter_type: FilterType.THRESHOLD,
            ThresholdFilterData_.threshold_type: ThresholdType.MANUAL,
        })
        mfd = dict_to_thresholdfilterdata(d)
        self.assertTrue(type(mfd) == ManualThresholdFilterData)

    def test_restore(self):
        mfd = ManualThresholdFilterData("id", FilterType.THRESHOLD, ThresholdType.MANUAL, "RGB", (100, 200))
        dict_ = asdict(mfd)
        restored = dict_to_thresholdfilterdata(dict_)
        self.assertEqual(mfd, restored)
