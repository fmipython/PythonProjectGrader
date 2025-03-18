"""
Factory for creating the checks objects.
"""

from grader.checks.abstract_check import AbstractCheck

from grader.checks.coverage_check import CoverageCheck
from grader.checks.pylint_check import PylintCheck
from grader.checks.requirements_check import RequirementsCheck
from grader.checks.structure_check import StructureCheck
from grader.checks.type_hints_check import TypeHintsCheck
from grader.utils.config import InvalidConfigError


NAME_TO_CHECK: dict[str, type[AbstractCheck]] = {
    "coverage": CoverageCheck,
    "pylint": PylintCheck,
    "requirements": RequirementsCheck,
    "type-hints": TypeHintsCheck,
    "structure": StructureCheck,
}


def create_checks(config: dict, project_root: str) -> tuple[list[AbstractCheck], list[AbstractCheck]]:
    """
    Build two lists, containing the non-venv checks and the venv checks.

    :param config: The configuration dictionary.
    :type config: dict
    :param project_root: The root of the project.
    :type project_root: str
    :raises InvalidConfigError: If no checks are found in the configuration file.
    :raises InvalidCheckError: If the check name is unknown.
    :return: A tuple containing the non-venv checks and the venv checks.
    :rtype: tuple[list[AbstractCheck], list[AbstractCheck]]
    """
    if "checks" not in config:
        raise InvalidConfigError("No checks found in the configuration file")

    checks = config["checks"]

    non_venv_checks = []
    venv_checks = []
    for check in checks:
        if "name" not in check or "max_points" not in check:
            raise InvalidConfigError("Invalid check configuration")

        name = check["name"]

        if name not in NAME_TO_CHECK:
            raise InvalidCheckError(f"Unknown check name: {name}")

        is_venv = check.get("is_venv_required", False)

        other_args = {**check}
        del other_args["name"]

        check_class = NAME_TO_CHECK[name]
        created_check = check_class(name, project_root, **other_args)

        if is_venv:
            venv_checks.append(created_check)
        else:
            non_venv_checks.append(created_check)

    return non_venv_checks, venv_checks


class InvalidCheckError(Exception):
    """
    Custom exception for invalid check names.
    """
