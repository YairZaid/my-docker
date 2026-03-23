import sys
import os
import ctypes

# קבועים של Linux
CLONE_NEWUTS = 0x04000000  # namespace חדש ל-hostname

def set_hostname(hostname):
    # קוראים ישירות ל-syscall של Linux
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    result = libc.sethostname(hostname.encode(), len(hostname))
    if result != 0:
        raise OSError(f"sethostname failed")

def create_namespace():
    libc = ctypes.CDLL("libc.so.6", use_errno=True)
    # unshare יוצר namespace חדש עבור ה-process הנוכחי
    result = libc.unshare(CLONE_NEWUTS)
    if result != 0:
        raise OSError(f"unshare failed")

def run_container(args):
    pid = os.fork()

    if pid == 0:
        # child — יוצר namespace חדש ומשנה hostname
        create_namespace()
        set_hostname("container")
        os.execvp(args[0], args)
    else:
        # parent — מחכה שהchild יסיים
        _, status = os.waitpid(pid, 0)
        exit_code = os.waitstatus_to_exitcode(status)
        sys.exit(exit_code)

def main():
    if len(sys.argv) < 3:
        print("Usage: docker.py run <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "run":
        args = sys.argv[2:]
        run_container(args)
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()