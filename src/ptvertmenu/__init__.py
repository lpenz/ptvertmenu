#!/usr/bin/env python3
# Copyright (C) 2023 Leandro Lisboa Penz <lpenz@lpenz.org>
# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.


import logging
import os
import re
import subprocess
import tempfile
from contextlib import contextmanager
from time import sleep
from typing import Generator, Optional


def _log() -> logging.Logger:
    if not hasattr(_log, "logger"):
        setattr(_log, "logger", logging.getLogger(os.path.basename("diskimgtool")))
    logger: logging.Logger = getattr(_log, "logger")
    return logger


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[bytes]:
    _log().info(f'+ {" ".join(cmd)}')
    return subprocess.run(cmd, check=check)


def run_capture(cmd: list[str], check: bool = True) -> str:
    _log().info(f'+ {" ".join(cmd)}')
    return subprocess.check_output(cmd, encoding="ascii")


@contextmanager
def chdir(path: str) -> Generator[None, None, None]:
    _log().info(f"+ cd {path}")
    cwd = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        _log().info("+ cd -")
        os.chdir(cwd)


@contextmanager
def loopback_setup(image: str) -> Generator[str, None, None]:
    data = run_capture(["kpartx", "-a", "-v", image])
    for line in data.split("\n"):
        if line:
            _log().info(f"  {line}")
    try:
        m = re.search(r"add map (loop[0-9]+)p.*", data)
        if not m:
            raise Exception("regex didnt match")
        loop = f"/dev/mapper/{m.group(1)}"
        yield loop
    finally:
        run(["kpartx", "-d", image], check=False)
        run(["sync"])


@contextmanager
def mount(
    src: str,
    dst: str,
    mtype: str = "auto",
    bind: bool = False,
    args: Optional[list[str]] = None,
) -> Generator[None, None, None]:
    if bind:
        mtype = "none"
    c = ["mount", "-t", mtype]
    if bind:
        c.extend(["-o", "bind"])
    if args:
        c.extend(args)
    c.extend([src, dst])
    run(c)
    try:
        yield
    finally:
        for i in range(5):
            r = run(["umount", dst], check=False)
            if r.returncode == 0:
                return
            run(["lsof", dst], check=False)
            sleep(1)
        run(["umount", "-l", dst])


@contextmanager
def root_mounts(rootdir: str) -> Generator[None, None, None]:
    with mount("dev", f"{rootdir}/dev", mtype="devtmpfs"):
        with mount("devpts", f"{rootdir}/dev/pts", mtype="devpts"):
            with mount("tmpfs", f"{rootdir}/dev/shm", mtype="tmpfs"):
                with mount("proc", f"{rootdir}/proc", mtype="proc"):
                    with mount("sysfs", f"{rootdir}/sys", mtype="sysfs"):
                        with mount("tmpfs", f"{rootdir}/run", mtype="tmpfs"):
                            dirs = [f"{rootdir}/run/lock", f"{rootdir}/run/shm"]
                            run(["mkdir", "-p"] + dirs)
                            yield


def chroot(rootdir: str, cmd: list[str]) -> subprocess.CompletedProcess[bytes]:
    cmd = ["chroot", rootdir] + cmd
    return run(cmd)


@contextmanager
def image_fully_mounted(image: str) -> Generator[str, None, None]:
    with tempfile.TemporaryDirectory(dir=os.getcwd()) as rootdir:
        with loopback_setup(image) as loop:
            with mount(f"{loop}p2", rootdir):
                with mount(f"{loop}p1", f"{rootdir}/boot"):
                    yield rootdir
