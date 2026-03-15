import asyncio
import signal

from tele_acp.types import Config, TelegramUserChannel

from .app import APP

config = Config(channels=[TelegramUserChannel(id="default", session_name="a7321e7c-e74e-49f9-9e74-38967d1fb0f0")])
app = APP(config)


async def main():
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, app.shutdown)

    await app.startup()


if __name__ == "__main__":
    asyncio.run(main())
