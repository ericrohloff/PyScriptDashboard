import js
from pyodide.ffi import create_proxy
from widgets import *


class UITracker:
    def __init__(s, widgetList):
        # dictionary to store all created widgets
        s.widgetBank = None

        widgetMenu = js.document.querySelector(".widget-adder__menu")

        # TODO: iterate through widget list and add their menu elements to
        for widgetClass in widgetList:
            widgetMenuElem = widgetClass._genMenuElem()
            widgetMenu.appendChild(widgetMenuElem)
            widgetMenuElem.addEventListener(
                "click", create_proxy(lambda evt: s.genWidget(evt, widgetClass)))

    def genWidget(s, evt, widgetClass):
        # calculate mouse position in the front panel
        fpBounds = js.document.querySelector(
            '[data-page="front-panel"]').getBoundingClientRect()

        initX = evt.clientX-fpBounds.left
        initY = evt.clientY-fpBounds.top

        newElem = widgetClass(initX, initY)
        # TODO: track new elem
