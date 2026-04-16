import ctypes
import os

MS_BIND = 4096
MS_REC = 16384
MS_PRIVATE = 1 << 18
MNT_DETACH = 2
SYS_PIVOT_ROOT = 155  # x86_64 syscall number for pivot_root

def setup_rootfs():
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    
    res = libc.mount(b"none", b"/", None, MS_REC | MS_PRIVATE, None)
    if res != 0:
        raise OSError(f"mount / private failed: {os.strerror(ctypes.get_errno())}")
        
    rootfs = b"/home/yair/docker-project/alpine-rootfs"
    res = libc.mount(rootfs, rootfs, b"bind", MS_BIND | MS_REC, None)
    if res != 0:
        raise OSError(f"bind mount rootfs failed: {os.strerror(ctypes.get_errno())}")
        
    put_old = os.path.join(rootfs.decode(), ".put_old")
    if not os.path.exists(put_old):
        os.makedirs(put_old)
        
    res = libc.syscall(SYS_PIVOT_ROOT, rootfs, put_old.encode())
    if res != 0:
        raise OSError(f"pivot_root failed: {os.strerror(ctypes.get_errno())}")
        
    os.chdir("/")
    
    res = libc.umount2(b"/.put_old", MNT_DETACH)
    if res != 0:
        raise OSError(f"umount2 failed: {os.strerror(ctypes.get_errno())}")
    os.rmdir("/.put_old")
    
    if not os.path.exists("/proc"):
        os.makedirs("/proc")
    res = libc.mount(b"proc", b"/proc", b"proc", 0, None)
    if res != 0:
        raise OSError(f"mount /proc failed: {os.strerror(ctypes.get_errno())}")
