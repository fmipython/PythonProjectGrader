"""
Module containing the unit test code coverage check.
"""

import logging
import os

from grader.checks.abstract_check import AbstractCheck
from grader.utils.constants import (
    COVERAGE_PATH,
    COVERAGE_RUN_ARGS,
    COVERAGE_RUN_PYTEST_ARGS,
    COVERAGE_REPORT_ARGS,
    COVERAGE_REPORT_ARGS_NO_FORMAT,
)
from grader.utils.files import find_all_source_files
from grader.utils.process import run

logger = logging.getLogger("grader")


class CoverageCheck(AbstractCheck):
    """
    The Coverage check class.
    """

    def __init__(self, name: str, max_points: int, project_root: str):
        super().__init__(name, max_points, project_root)

        self.__coverage_full_path = os.path.join(project_root, COVERAGE_PATH)

    def run(self) -> float:
        """
        Run the coverage check on the project.

        :returns: The score from the coverage check.
        :rtype: float
        """
        super().run()

        is_coverage_run_okay = self.__coverage_run()

        if not is_coverage_run_okay:
            return 0.0

        coverage_report_result = self.__coverage_report()

        if coverage_report_result is None:
            return 0.0

        return self.__translate_score(coverage_report_result)

    def __translate_score(self, coverage_score: float) -> float:
        """
        Split the coverage score into regions and assign a score based on the region.
        The amount of regions depends on the max points for the criteria.

        :param coverage_score: The score from pylint to be translated
        :return: The translated score
        """
        step = 100 / (self._max_points + 1)
        steps = [i * step for i in range(self._max_points + 2)]

        regions = list(zip(steps, steps[1:]))

        for score, (start, end) in enumerate(regions):
            if start <= coverage_score < end:
                return score

        return self._max_points

    def __coverage_run(self):
        """
        Run the coverage tool on the project.
        """
        command = [self.__coverage_full_path] + COVERAGE_RUN_ARGS + COVERAGE_RUN_PYTEST_ARGS + [self._project_root]

        output = run(command, current_directory=self._project_root)

        if output.returncode != 0:
            logger.error("Coverage run failed")
            return False

        return True

    def __coverage_report(self):
        """
        Generate a report from the coverage tool.
        """
        source_files = find_all_source_files(self._project_root)

        command = [self.__coverage_full_path] + COVERAGE_REPORT_ARGS_NO_FORMAT + source_files
        output = run(command, current_directory=self._project_root)

        command = [self.__coverage_full_path] + COVERAGE_REPORT_ARGS + source_files
        output = run(command, current_directory=self._project_root)

        if output.returncode != 0:
            logger.error("Coverage report failed")
            return None

        return int(output.stdout)
