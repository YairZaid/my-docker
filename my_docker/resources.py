import os
import sys

def setup_cgroups(container_pid):
    cgroup_dir = "/sys/fs/cgroup/mydocker"
    try:
        if not os.path.exists(cgroup_dir):
            os.makedirs(cgroup_dir)
        with open(os.path.join(cgroup_dir, "memory.max"), "w") as f:
            f.write("50000000")
        with open(os.path.join(cgroup_dir, "pids.max"), "w") as f:
            f.write("20")
        with open(os.path.join(cgroup_dir, "cgroup.procs"), "w") as f:
            f.write(str(container_pid))
    except Exception as e:
        print(f"Warning: Cgroup setup failed - {e}", file=sys.stderr)
