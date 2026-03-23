import sys
import os

def main():
    if len(sys.argv) < 3:
        print("Usage: docker.py run <command>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "run":
        args = sys.argv[2:]
        pid = os.fork()

        if pid == 0:
            # child process — מריץ את הפקודה
            os.execvp(args[0], args)
        else:
            # parent process — מחכה שהילד יסיים
            _, status = os.waitpid(pid, 0)
            exit_code = os.waitstatus_to_exitcode(status)
            sys.exit(exit_code)

if __name__ == "__main__":
    main()