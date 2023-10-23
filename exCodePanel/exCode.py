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

####################

b0 = getButton(0)
l0 = getLed(0)


def myCallback():
    l0.toggle()


b0.setCallback(myCallback)

#################

upButton = getButton(0)
downButton = getButton(1)


leds = [getLed(i) for i in range(8)]


def increment():
    global leds
    for led in leds:
        if led.isOn:
            led.turnOff()
        else:
            led.turnOn()
            break


def decrement():
    global leds
    for led in leds:
        if not led.isOn:
            led.turnOn()
        else:
            led.turnOff()
            break


upButton.setCallback(increment)
downButton.setCallback(decrement)
