import js
from pyodide.ffi import create_proxy
from widgets import *


class UITracker:
    def __init__(s, widgetList):

        widgetMenu = js.document.querySelector(".widget-adder__menu")

        # Iterate through widget list and add their menu elements to menu
        for widgetClass in widgetList:
            widgetMenuElem = widgetClass._genMenuElem()
            widgetMenu.appendChild(widgetMenuElem)

    def getWidget(s, className, index):
        return className.widgets[index]


# TODO: make a way to reference widgets
