# Custom Python Docker Engine: Architecture Deep Dive

## 1. Overview
This project is a custom container runtime engine built entirely from scratch in Python. It mimics the underlying Linux isolation systems used by enterprise platforms like Docker and runc.

## 2. Platform Architecture 
We structurally refactored the engine from a monolithic script into a clean, decoupled Python package (`my_docker/`), isolating concerns efficiently:

- `docker.py`: A lightweight CLI wrapper mapping execution natively.
- `my_docker/main.py`: Parses terminal input and acts as the entrypoint.
- `my_docker/container.py`: Manages the application lifecycle. Coordinates the namespace unsharing and executes the "double-fork" orchestration necessary for mapping PID 1.
- `my_docker/namespaces.py`: Generates the unshared environments interacting strictly via `ctypes.CDLL`.
- `my_docker/storage.py`: Forces execution inside an Alpine filesystem using `pivot_root`.
- `my_docker/resources.py`: Implements aggressive Control Group hardware abstractions.
- `my_docker/network.py`: Limits internet protocols establishing a firewall perimeter offline.

## 3. Technology and Logic Deep Dive

### A. Namespace Isolation
We use `libc.unshare` inside a disposable intermediate process context to prevent mutating the overarching host environment.
- **Hostnames (`CLONE_NEWUTS`)**: Uncouples the shell hostname allowing us to disguise the system as `container`.
- **Mounts (`CLONE_NEWNS`)**: Guarantees disk mapping actions stay constrained to the container map.
- **Networks (`CLONE_NEWNET`)**: Unbinds virtual machines from the internet seamlessly, booting natively offline locally.
- **Processes (`CLONE_NEWPID`)**: Detaches the process tree placing the shell effectively in `PID 1`. We execute a secondary `fork()` directly after unsharing to physically cross the boundary securely.

### B. Hard Storage Isolation (`pivot_root` over `chroot`)
Using `chroot` is infamous for generating security jailbreaks where malicious users tunnel upward. We completely sever that connection.
1. `MS_PRIVATE` modifies the entire local scope to intercept rogue bind points.
2. The `alpine-rootfs` directory is statically bind-mounted vertically to itself creating a standalone system device.
3. We execute Syscall `155` (`pivot_root`) permanently overwriting our process environment natively into a clean alpine map.

### C. External Limits (Cgroups)
To completely prevent the container from collapsing the host Ubuntu Operating System (such as through Out-Of-Memory attacks or Fork Bombs), we write hardware commands to `/sys/fs/cgroup/mydocker`.
1. `memory.max`: Handed a `50MB` cap limit enforced strictly by the Kernel.
2. `pids.max`: Given a max sequence of 20 relative tasks to exterminate loops gracefully.
