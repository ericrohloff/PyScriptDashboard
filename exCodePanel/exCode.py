from uiInterface import getButton, getLed, getCanvas, getCamera
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


######

snapButton = getButton(0)
processButton = getButton(1)

camera = getCamera(0)
canvas = getCanvas(0)

snapButton.setCallback(camera.snap)


def process():
    data = camera.lastSnap
    data[:, :, 0] = 0
    data[:, :, 1] = 0
    canvas.renderImage(data)


processButton.setCallback(process)

####

i = getImageFrame(0)
b = getButton(0)
c = getCamera(0)


def snap():
    img = c.snap()
    cv2_image = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    grey = cv2.cvtColor(cv2_image, cv2.COLOR_BGRA2GRAY)
    blurred = cv2.GaussianBlur(grey, (5, 5), 0)
    thresh = cv2.threshold(blurred, 200, 255, cv2.THRESH_BINARY)[1]
    i.displayCv2(thresh)


b.setCallback(snap)
