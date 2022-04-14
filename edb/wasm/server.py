import asyncio
import logging
import os
import pathlib
import socket
import sys


log = logging.getLogger(__name__)


class Protocol(asyncio.SubprocessProtocol):

    def process_exited(self):
        log.error("WASM process exites")


class WasmServer:
    _loop: asyncio.AbstractEventLoop
    _process: asyncio.SubprocessTransport | None
    _sock_path: pathlib.Path

    def __init__(self, sock_path: pathlib.Path):
        log.info("Starting WebAssembly server")
        self._loop = asyncio.get_running_loop()
        self._process = None
        self._sock_path = sock_path

        self._loop.create_task(self._start())

    async def _start(self):
        try:
            await self._start_inner()
        except Exception as e:
            log.exception("Error starting process:", exc_info=e)
            sys.exit(1)  # TODO(tailhook) is it a greatest way to solve this?

    async def _start_inner(self):
        thisdir = pathlib.Path(__file__).parent
        if self._sock_path.exists():
            os.unlink(self._sock_path)
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        sock.bind(str(self._sock_path))
        sock.listen()
        cmdline = [
            str(thisdir / 'edgedb-wasm-server'),
            "--fd=0",
        ]
        transport, _ = await self._loop.subprocess_exec(
            Protocol,
            *cmdline,
            stdin=sock,
            stdout=None,
            stderr=None,
        )
        sock.close()
        self._process = transport
