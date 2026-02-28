import asyncio
import logging
from asyncio import timeout

from aiohttp import ClientSession, ClientError

_LOGGER = logging.getLogger(__name__)


class SmartWBApi:
    def __init__(self, session: ClientSession, ip: str, port: int):
        self._session = session
        self._ip = ip
        self._port = port
        self._lock = asyncio.Lock()

    @property
    def base_url(self) -> str:
        return f"http://{self._ip}:{self._port}"

    async def get_parameters(self) -> dict:
        url = f"{self.base_url}/getParameters"
        async with self._lock:
            try:
                async with timeout(10):
                    async with self._session.get(url) as resp:
                        resp.raise_for_status()
                        data = await resp.json()
                        return data["list"][0]
            except (ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Error fetching parameters from %s: %s", url, e)
                raise

    async def set_current(self, current: int) -> str:
        url = f"{self.base_url}/setCurrent?current={current}"
        async with self._lock:
            try:
                async with timeout(10):
                    async with self._session.get(url) as resp:
                        resp.raise_for_status()
                        text = await resp.text()
                        return text
            except (ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Error setting current via %s: %s", url, e)
                raise

    async def set_always_active(self, active: bool) -> str:
        value = 1 if active else 0
        url = f"{self.base_url}/setAlwaysActive?active={value}"
        async with self._lock:
            try:
                async with timeout(10):
                    async with self._session.get(url) as resp:
                        resp.raise_for_status()
                        text = await resp.text()
                        return text
            except (ClientError, asyncio.TimeoutError) as e:
                _LOGGER.error("Error setting alwaysActive via %s: %s", url, e)
                raise