#!/usr/bin/env python3
"""portcheck —— 一个极小的 TCP 端口探测工具。

用法：
    python3 portcheck.py <主机> <端口> [更多端口...]
    python3 portcheck.py 127.0.0.1 22 80 443

退出码：全通为 0，有任意一个不通为 1。方便写进脚本里做等待判断。

只做一次 connect，不做超时重试 —— 需要重试请在外层循环。
"""

from __future__ import annotations

import socket
import sys
import time


def check(host: str, port: int, timeout: float = 2.0) -> tuple[bool, float]:
    """尝试连接 host:port，返回 (是否连通, 耗时秒数)。"""
    start = time.monotonic()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.connect((host, port))
        except (OSError, socket.timeout):
            return False, time.monotonic() - start
    return True, time.monotonic() - start


def main(argv: list[str]) -> int:
    if len(argv) < 3:
        print(__doc__.strip())
        return 2

    host = argv[1]
    try:
        ports = [int(p) for p in argv[2:]]
    except ValueError:
        print(f"端口必须是整数：{argv[2:]}", file=sys.stderr)
        return 2

    failed = 0
    for port in ports:
        ok, elapsed = check(host, port)
        mark = "open  " if ok else "closed"
        print(f"{mark}  {host}:{port}  {elapsed * 1000:.0f} ms")
        if not ok:
            failed += 1

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
