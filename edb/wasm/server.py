import asyncio
import dataclasses
import logging
import os
import pathlib
import socket
import sys
import weakref

from edb.common import debug
from edb.wasm import wasm_ext


log = logging.getLogger(__name__)


@dataclasses.dataclass
class SetDirectory:
    database: str
    directory: str


class Protocol(asyncio.SubprocessProtocol):

    def process_exited(self):
        log.error("WASM process exites")


class WasmServer:
    _loop: asyncio.AbstractEventLoop
    _process: asyncio.SubprocessTransport | None
    _sock_path: pathlib.Path
    _server: weakref.ref
    _config_queue: asyncio.Queue

    def __init__(self, server, sock_path: pathlib.Path):
        self._server = weakref.ref(server)
        self._loop = asyncio.get_running_loop()
        self._process = None
        self._sock_path = sock_path
        self._config_queue = asyncio.Queue()

        self._loop.create_task(self._start())

    def set_dir(self, dbname: str, path: pathlib.Path):
        self._config_queue.put_nowait(SetDirectory(dbname, str(path)))

    async def _start(self):
        try:
            await self._start_inner()
        except Exception as e:
            log.exception("Error starting process:", exc_info=e)
            sys.exit(1)  # TODO(tailhook) is it a greatest way to solve this?

    async def _start_inner(self):
        if debug.flags.skip_wasm_server_start:
            log.info("WebAssembly server is skipped "
                     "(assumed to be started externally)")
            self._loop.create_task(self._config_task())
            return
        log.info("Starting WebAssembly server")
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
        self._loop.create_task(self._config_task())

    async def _config_task(self):
        while True:
            config = await self._config_queue.get()
            match config:  # flake8: noqa (syntax is not supported yet)
                case SetDirectory(database, directory):
                    await wasm_ext.rpc_request(
                        self._server(),
                        "set_directory",
                        dict(
                            database=database,  # noqa: F821
                            directory=directory,  # noqa: F821
                        )
                    )
