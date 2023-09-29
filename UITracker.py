import js
from pyodide.ffi import create_proxy
from widgets import *


class UITracker:
    def __init__(s, widgetList):
        # dictionary to store all created widgets
        s.widgetBank = dict()

        widgetMenu = js.document.querySelector(".widget-adder__menu")

        # TODO: iterate through widget list and add their menu elements to menu
        for widgetClass in widgetList:
            widgetMenuElem = widgetClass._genMenuElem()
            widgetMenu.appendChild(widgetMenuElem)
            widgetMenuElem.addEventListener(
                "click", create_proxy(lambda evt: s.genWidget(evt, widgetClass)))

    def genWidget(s, evt, widgetClass):

        # temp: prompt user for a name off the rip and it wont be able to be changed
        name = js.prompt("please enter a name for the widget:")

        if not name:
            return

        # calculate mouse position in the front panel
        fpBounds = js.document.querySelector(
            '[data-page="front-panel"]').getBoundingClientRect()

        initX = evt.clientX-fpBounds.left
        initY = evt.clientY-fpBounds.top

        newWidget = widgetClass(initX, initY)

        # temp: assign widget given name
        newWidget.element.querySelector(".UIElement__name").value = name
        s.widgetBank[name] = newWidget

        # TODO: track new elem
        # TODO: somehow track name changes from this class

    def getWidget(s, widgetName):
        return s.widgetBank[widgetName]
