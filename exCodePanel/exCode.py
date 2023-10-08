import time
import asyncio
b0 = getButton(0)
l0 = getLed(0)


async def main():
    while True:
        if b0.isActive():
            l0.turnOn()
        else:
            l0.turnOff()
        await asyncio.sleep(0.1)

asyncio.create_task(main())
