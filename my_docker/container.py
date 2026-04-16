import os
import sys

from my_docker.namespaces import create_namespace, set_hostname
from my_docker.storage import setup_rootfs
from my_docker.resources import setup_cgroups
from my_docker.network import setup_network

def run_container(args):
    # First fork: Create an intermediate process to establish constraints
    pid = os.fork()

    if pid == 0:
        # Intermediate process - sets up the namespaces
        create_namespace()
        
        # Second fork: The new child will be placed into the newly created PID namespace as PID 1
        container_pid = os.fork()
        if container_pid == 0:
            # Inside the final container process (PID 1)
            set_hostname("container")
            setup_rootfs()
            setup_network()
            
            os.execvp(args[0], args)
        else:
            # Intermediate process isolates the container resources and waits
            setup_cgroups(container_pid)
            _, status = os.waitpid(container_pid, 0)
            sys.exit(os.waitstatus_to_exitcode(status))
    else:
        # parent - waits for the child to finish
        _, status = os.waitpid(pid, 0)
        exit_code = os.waitstatus_to_exitcode(status)
        sys.exit(exit_code)
