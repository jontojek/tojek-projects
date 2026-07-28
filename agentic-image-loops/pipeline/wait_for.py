#!/usr/bin/env python3
"""Block until a file exists (and has stopped growing), then exit.

Turns "waiting for the runner" into a single executable action for the agent:

  python wait_for.py <path> [--timeout 120]

Exit code 0 = file is ready. Exit code 1 = timed out (report to human).
"""
import argparse
import os
import sys
import time


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("path")
    ap.add_argument("--timeout", type=float, default=120.0)
    args = ap.parse_args()

    deadline = time.time() + args.timeout
    last_size = -1
    while time.time() < deadline:
        if os.path.exists(args.path):
            size = os.path.getsize(args.path)
            if size > 0 and size == last_size:  # exists and finished writing
                print(f"READY {args.path} ({size} bytes)")
                return 0
            last_size = size
        time.sleep(1.0)
    print(f"TIMEOUT after {args.timeout}s waiting for {args.path}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
