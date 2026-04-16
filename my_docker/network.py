import os

def setup_network():
    # Start loopback interface silently using busybox iproute
    os.system("ip link set lo up 2>/dev/null")
