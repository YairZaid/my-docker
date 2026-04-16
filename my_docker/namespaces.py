import ctypes
import os

CLONE_NEWUTS = 0x04000000  # New namespace for hostname
CLONE_NEWPID = 0x20000000  # New namespace for process IDs
CLONE_NEWNS  = 0x00020000  # New namespace for mount points
CLONE_NEWNET = 0x40000000  # New namespace for network devices

def set_hostname(hostname):
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    result = libc.sethostname(hostname.encode(), len(hostname))
    if result != 0:
        raise OSError(f"sethostname failed")

def create_namespace():
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    flags = CLONE_NEWUTS | CLONE_NEWPID | CLONE_NEWNS | CLONE_NEWNET
    result = libc.unshare(flags)
    if result != 0:
        raise OSError(f"unshare failed: {os.strerror(ctypes.get_errno())}")
