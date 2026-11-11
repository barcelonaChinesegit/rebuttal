"""Small mathematical regression checks; all fixtures are synthetic."""
import math
import tempfile
import unittest
from pathlib import Path
from judge_audit_analysis import kappa, kappa3, spearman, kendall, read_labels


class StatisticsTests(unittest.TestCase):
    def test_balanced_binary_kappa(self):
        # Both marginals are 1/2; observed agreement 3/4 gives kappa 1/2.
        self.assertAlmostEqual(kappa([0,0,0,0,1,1,1,1], [0,0,0,1,0,1,1,1])[0], .5)

    def test_spearman_uses_average_ranks_for_ties(self):
        self.assertAlmostEqual(spearman([1,1,2], [1,2,3]), math.sqrt(.75))
        self.assertAlmostEqual(spearman([1,2,3], [3,2,1]), -1)

    def test_constant_labels_are_undefined_not_perfect(self):
        self.assertTrue(math.isnan(kappa([1,1], [1,1])[0]))
        self.assertTrue(math.isnan(kappa3([2,2], [2,2])))
        self.assertTrue(math.isnan(spearman([1,1], [2,3])))
        self.assertTrue(math.isnan(kendall([1,1], [2,3])))

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'labels.csv'
            p.write_text('编号,标注\nA1,正确\nA1,错误\n')
            with self.assertRaises(SystemExit):
                read_labels(str(p))

    def test_missing_labels_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'labels.csv'
            p.write_text('编号,标注\nA1,\n')
            with self.assertRaises(SystemExit):
                read_labels(str(p))


if __name__ == '__main__':
    unittest.main()
