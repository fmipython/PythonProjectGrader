import unittest
from subprocess import CompletedProcess
from unittest.mock import patch, MagicMock

from grader.checks.coverage_check import CoverageCheck


class TestCoverageCheck(unittest.TestCase):
    def setUp(self):
        self.coverage_check = CoverageCheck("Coverage", 2, "sample_dir")
        # This way, we have 3 ranges: 0-33, 34-66, 67-100
        return super().setUp()

    @patch("subprocess.run")
    def test_01_coverage_run_fail(self, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = CompletedProcess(args=["coverage", "run"], returncode=1)

        # Act
        with self.assertLogs("grader", level="ERROR") as log:
            result = self.coverage_check.run()
            is_message_logged = "ERROR:grader:Coverage run failed" in log.output

        # Assert
        self.assertEqual(0.0, result)
        self.assertTrue(is_message_logged)

    @patch("subprocess.run")
    def test_02_coverage_report_fail(self, mocked_run: MagicMock):
        # Arrange
        def mocked_run_side_effect(*args, **kwargs):
            if "run" in args[0]:
                return CompletedProcess(args=["coverage", "run"], returncode=0)
            if "report" in args[0]:
                return CompletedProcess(args=["coverage", "report"], returncode=1)

        mocked_run.side_effect = mocked_run_side_effect
        # Act
        with self.assertLogs("grader", level="ERROR") as log:
            result = self.coverage_check.run()
            is_message_logged = "ERROR:grader:Coverage report failed" in log.output

        # Assert
        self.assertEqual(0.0, result)
        self.assertTrue(is_message_logged)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_03_translate_score_zero(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 0
        expected_score = 0

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_04_translate_score_inside_first_range(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 22
        expected_score = 0

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_05_translate_score_right_bound_first_range(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100 / 3
        expected_score = 1

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_06_translate_score_left_bound_second_range(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100 / 3 + 1
        expected_score = 1

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_07_translate_score_inside_bound_second_range(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 50
        expected_score = 1

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_08_translate_score_right_bound_second_range(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100 / 3 * 2
        expected_score = 2

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_09_translate_score_inside_bound_third_range(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 75
        expected_score = 2

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_run")
    @patch("grader.checks.coverage_check.CoverageCheck._CoverageCheck__coverage_report")
    def test_10_translate_score_max(self, mocked_report: MagicMock, mocked_run: MagicMock):
        # Arrange
        mocked_run.return_value = True
        mocked_report.return_value = 100
        expected_score = 2

        # Act
        actual_score = self.coverage_check.run()

        # Assert
        self.assertEqual(expected_score, actual_score)

    @patch("subprocess.run")
    def test_11_coverage_report_read_properly(self, mocked_run: MagicMock):
        # Arrange
        def mocked_run_side_effect(*args, **kwargs):
            if "run" in args[0]:
                return CompletedProcess(args=["coverage", "run"], returncode=0)
            if "report" in args[0]:
                return CompletedProcess(args=["coverage", "report"], returncode=0, stdout="100")

        mocked_run.side_effect = mocked_run_side_effect
        # Act
        result = self.coverage_check.run()

        # Assert
        self.assertEqual(2, result)
