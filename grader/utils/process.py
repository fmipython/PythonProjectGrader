import logging
import subprocess

# from grader.utils.logger import VERBOSE

logger = logging.getLogger("grader")


def run(command):
    logger.debug("Running command: %s", command)
    output = subprocess.run(command, check=False, capture_output=True, text=True)

    if output.returncode != 0:
        logger.debug("Command failed: %d %s %s", output.returncode, output.stdout, output.stderr)
    else:
        logger.debug("Command succeeded: %s", output.stdout)
    return output