import js
from pyodide.ffi import create_proxy
from pyscript import when
from widgets import *
from UITracker import UITracker

tracker = UITracker([buttonWidget, LEDWidget, cameraWidget, canvasWidget])

# temp functions for testing

video = js.document.querySelector(".UIcamera")
camera_button = js.document.querySelector("#start-camera")
stopcam = js.document.querySelector("#stop-camera")
stream = None


async def camera_click(e):
    global stream
    media = js.Object.new()
    media.audio = False
    media.video = True
    stream = await js.navigator.mediaDevices.getUserMedia(media)
    video.srcObject = stream


async def stopit(e):
    stream.getTracks()[0].stop()

camera_button.addEventListener('click', create_proxy(camera_click))

stopcam.addEventListener('click', create_proxy(stopit))

canvas = js.document.querySelector("#canvas")
ctx = canvas.getContext("2d")


@when("click", selector="#snap")
def snapcam(evt):
    print("video width")
    print(video.videoWidth)
    print("video height")
    print(video.videoHeight)
    print("video offset width")
    print(video.offsetWidth)
    print("video offset height")
    print(video.offsetHeight)
    print("width")
    print(canvas.width)
    print("offset width")
    print(canvas.offsetWidth)
    print("height")
    print(canvas.height)
    print("offset height")
    print(canvas.offsetHeight)

    # ctx.scale(canvas.width/canvas.offsetWidth,
    #           canvas.height/canvas.offsetHeight)

    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    print("canvas width")
    print(canvas.width)
    print("canvas height")
    print(canvas.height)
    print("canvas offset width")
    print(canvas.offsetWidth)
    print("canvas offset height")
    print(canvas.offsetHeight)

    print("________________")
    ctx.moveTo(0, 0)
    ctx.drawImage(video, 0, 0, video.videoWidth, video.videoHeight)
    ctx.lineTo(200, 100)
    ctx.stroke()
    ctx.moveTo(0, 0)
    ctx.lineTo(100, 100)
    ctx.stroke()

######


def getButton(idx):
    return tracker.getWidget(buttonWidget, idx)


def getLed(idx):
    return tracker.getWidget(LEDWidget, idx)


@when("click", selector=".headBar__buttons__button.run")
def runMode(evt):
    if not evt.currentTarget.classList.contains("disabled"):
        tracker.enableRunMode()
        evt.currentTarget.classList.add("disabled")
        js.document.querySelector(
            ".headBar__buttons__button.stop").classList.remove("disabled")
        js.document.querySelector(
            ".widget-adder__menu").classList.remove("shown")


@when("click", selector=".headBar__buttons__button.stop")
def stopMode(evt):
    if not evt.currentTarget.classList.contains("disabled"):
        tracker.enableEditMode()
        evt.currentTarget.classList.add("disabled")
        js.document.querySelector(
            ".headBar__buttons__button.run").classList.remove("disabled")


@when("click", selector=".widget-adder__button")
def toggleButtonAdderMenu(evt):
    # only allow menu opening if program is able to run (in edit mode)
    # will make this handled in a more elegant way in future updates
    menu = evt.currentTarget.parentElement.querySelector(".widget-adder__menu")
    if not js.document.querySelector(".headBar__buttons__button.run").classList.contains("disabled"):
        menu.classList.toggle("shown")


@when("click", selector=".headBar__tabs__tab")
def toggleFrontPanel(evt):
    # find which tab was clicked and its associated page
    targetPage = evt.currentTarget.getAttribute("data-page-target")
    # loop through pages and hide them, but show the target page
    for page in js.document.querySelectorAll(".pageContent__content"):
        if page.getAttribute("data-page") == targetPage:
            page.classList.add("shown")
        else:
            page.classList.remove("shown")

    # remove selected style from previously selected tab and add to new one
    for tab in js.document.querySelectorAll(".headBar__tabs__tab"):
        if tab == evt.currentTarget:
            tab.classList.add("selected")
        else:
            tab.classList.remove("selected")
