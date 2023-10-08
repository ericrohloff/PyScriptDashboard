import js
from pyodide.ffi import create_proxy
from pyscript import when
from widgets import *
from UITracker import UITracker

tracker = UITracker([buttonWidget, LEDWidget])

# temp function for testing


def getButton(idx):
    return tracker.getWidget(buttonWidget, idx)


def getLed(idx):
    return tracker.getWidget(LEDWidget, idx)


@when("click", selector=".widget-adder__button")
def toggleButtonAdderMenu(evt):
    evt.currentTarget.parentElement.querySelector(
        ".widget-adder__menu").classList.toggle("shown")


@when("click", selector=".headBar__tab")
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
    for tab in js.document.querySelectorAll(".headBar__tab"):
        if tab == evt.currentTarget:
            tab.classList.add("selected")
        else:
            tab.classList.remove("selected")
