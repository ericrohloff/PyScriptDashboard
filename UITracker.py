import js
from pyodide.ffi import create_proxy
from widgets import *


class UITracker:
    def __init__(s, widgetList):

        s.widgetList = widgetList
        s.savedData = None

        widgetMenu = js.document.querySelector(".widget-adder__menu")

        # Iterate through widget list and add their menu elements to menu
        for widgetClass in widgetList:
            widgetMenuElem = widgetClass._genMenuElem()
            widgetMenu.appendChild(widgetMenuElem)

        # make event listener for double click on front panel
        js.document.querySelector("[data-page='front-panel']").addEventListener(
            "dblclick", create_proxy(textWidget._genWidget))

    def getWidget(s, className, index):
        return className.widgets[index]

    def enableRunMode(s):
        for widgetClass in s.widgetList:
            widgetClass.enableRunMode()
        textWidget.enableRunMode()

    def enableEditMode(s):
        for widgetClass in s.widgetList:
            widgetClass.enableEditMode()
        textWidget.enableEditMode()

    def saveData(s):
        data = {}
        for widgetClass in s.widgetList:
            data[widgetClass.__name__] = widgetClass.saveData()
        data[textWidget.__name__] = widgetClass.saveData()
        print(data)
        s.savedData = data

    def loadData(s):
        for widgetClass in s.widgetList:
            widgetClass.loadData(copy.deepcopy(
                s.savedData[widgetClass.__name__]))
        textWidget.loadData(copy.deepcopy(
            s.savedData[textWidget.__name__]))
