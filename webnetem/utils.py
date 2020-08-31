import subprocess
import shlex


def logger():
    from webnetem.server import app

    return app.logger


def call(command):
    """Run command.
    """
    logger().debug(command)
    subprocess.call(command, shell=True)


def check_call(command):
    """Run command, raising CalledProcessError if it fails.
    """
    logger().debug(command)
    subprocess.check_call(command, shell=True)
