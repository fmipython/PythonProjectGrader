import logging
import os
import shutil
import subprocess

from grader.utils.constants import REQUIREMENTS_FILENAME
from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")


class VirtualEnvironment:
    def __init__(self, project_path: str):
        self._project_path = project_path
        self._venv_path = os.path.join(project_path, ".venv")

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.teardown()

    def setup(self):
        # Check for existing venv
        possible_venv_paths = [os.path.join(self._project_path, "venv"), os.path.join(self._project_path, ".venv")]

        for path in possible_venv_paths:
            if os.path.exists(path):
                logger.log(VERBOSE, "Found existing venv at %s", path)
                shutil.rmtree(path)

        # Check for requirements.txt
        requirements_path = os.path.join(self._project_path, REQUIREMENTS_FILENAME)

        does_requirements_exist = os.path.exists(requirements_path)
        if not does_requirements_exist:
            logger.error("No requirements.txt file found in the project directory")

        # Create new venv
        logger.log(VERBOSE, "Creating new venv")

        # TODO - Assuming python3 is valid
        subprocess.run(["python", "-m", "venv", self._venv_path], check=False, capture_output=True)

        # Install requirements
        if does_requirements_exist:
            logger.log(VERBOSE, "Installing requirements")
            VirtualEnvironment.__install_requirements(self._venv_path, requirements_path)

        # Install grader dependencies
        logger.log(VERBOSE, "Installing grader dependencies")
        # TODO - This needs fixing
        grader_requirements_path = os.path.join(os.path.dirname(__file__), "grader_requirements.txt")
        VirtualEnvironment.__install_requirements(self._venv_path, grader_requirements_path)

        # TODO - Missing error handling

    def teardown(self):
        # subprocess.run(["deactivate"], check=False, capture_output=True)
        # shutil.rmtree(self._venv_path)
        pass

    @staticmethod
    def __install_requirements(venv_path: str, requirements_path: str):
        pip_path = os.path.join(venv_path, "Scripts", "pip.exe")  # TODO - Replace with OS agnostic solution
        output = subprocess.run([pip_path, "install", "-r", requirements_path], check=False, capture_output=True)
