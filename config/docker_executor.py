from autogen_ext.code_executors.docker import DockerCommandLineCodeExecutor
from config.constant import *

def get_docker_executor():
    """
    Function to get docker executor.
    This executor is responsible for executing code in a docker container.
    """
    docker_executor = DockerCommandLineCodeExecutor(
        work_dir=WORK_DIR,
        timeout=TIMEOUT
    )
    return docker_executor