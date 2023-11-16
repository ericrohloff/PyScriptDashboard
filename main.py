import js
from pyodide.ffi import create_proxy
from pyscript import when
from widgets import *
from UITracker import UITracker

tracker = UITracker([buttonWidget, LEDWidget, cameraWidget,
                    canvasWidget, imageFrameWidget])

# temp functions for testing


@when("click", selector="#save")
def test(evt):
    tracker.saveData()


@when("click", selector="#load")
def test(evt):
    tracker.loadData()
######


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
