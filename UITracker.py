import js
from pyodide.ffi import create_proxy
from widgets import *


class UITracker:
    def __init__(s, widgetList):

        s.widgetList = widgetList

        widgetMenu = js.document.querySelector(".widget-adder__menu")

        # Iterate through widget list and add their menu elements to menu
        for widgetClass in widgetList:
            widgetMenuElem = widgetClass._genMenuElem()
            widgetMenu.appendChild(widgetMenuElem)

    def getWidget(s, className, index):
        return className.widgets[index]

    def enableRunMode(s):
        for widgetClass in s.widgetList:
            widgetClass.enableRunMode()

    def enableEditMode(s):
        for widgetClass in s.widgetList:
            widgetClass.enableEditMode()

    def saveData(s):
        data = {}
        for widgetClass in s.widgetList:
            data[widgetClass.__name__] = widgetClass.saveData()

        print(data)
        s.saveData = data

    def loadData(s):
        for widgetClass in s.widgetList:
            widgetClass.loadData(s.savedData[widgetClass.__name__])
