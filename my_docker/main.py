import sys
from my_docker.container import run_container

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
