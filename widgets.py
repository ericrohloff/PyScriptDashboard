import js
from pyodide.ffi import create_proxy
from pyscript import when
import heapq
from abc import ABC, abstractmethod


class UIElement(ABC):
    # These need to be overridden
    widgets = []  # abstract
    availableIndexes = []  # abstract
    numWidgets = 0  # abstract

    def __init__(s, initX, initY):
        s.element = js.document.createElement("div")

        s.frontPanel = js.document.querySelector("[data-page='front-panel']")
        s.frontPanel.appendChild(s.element)
        s.element.classList.add("UIElement")

        # position element under mouse
        s.element.style.left = f"{initX}px"
        s.element.style.top = f"{initY}px"
        s.element.style.transform = "translate(-50%, -50%)"

        s.element.innerHTML = s.elemHtml
        # save drag callback proxies so they can be added and removed
        s._dragElemProxy = create_proxy(s._dragElem)

        # add drag event listeners
        s.element.addEventListener("mousedown", create_proxy(s._startDrag))
        js.document.addEventListener("mouseup", create_proxy(s._stopDrag))

        # menu toggle
        s.element.querySelector(".UIElement__caret").addEventListener(
            "click", create_proxy(s._toggleMenu))

        # remove element event
        s.element.querySelector(
            "[data-function='delete']").addEventListener("click", create_proxy(s._deleteWidget))

        # track widget in class attributes
        s._trackNewWidget()

    def _trackNewWidget(s):
        # should be called after new widget is created in subclass to properly give
        # the element an ID.
        if not s.__class__.availableIndexes:
            s.index = s.__class__.numWidgets
        else:
            s.index = heapq.heappop(s.__class__.availableIndexes)

        s.__class__.numWidgets += 1
        s.__class__.widgets.insert(s.index, s)

    def _deleteWidget(s, evt):
        # event listener for delete button in dropdown menu
        if not js.window.confirm("Are you sure you want to remove the widget?"):
            return

        s.element.parentNode.removeChild(s.element)
        s.__class__.numWidgets -= 1
        heapq.heappush(s.__class__.availableIndexes, s.index)
        s.__class__.widgets[s.index] = None

    def _dragElem(s, evt):
        # event listener for mouse movement to move widget

        evt.movementX
        elemStyles = js.window.getComputedStyle(s.element)

        # temp
        if not "px" in elemStyles.left:
            print("_dragElem: no px in left style")

        # may need to change to regex if more robust parsing needed
        leftStart = int(elemStyles.left.rstrip("px"))
        topStart = int(elemStyles.top.rstrip("px"))

        s.element.style.left = f"{evt.movementX + leftStart}px"
        s.element.style.top = f"{evt.movementY + topStart}px"

    def _startDrag(s, evt):
        js.document.addEventListener("mousemove", s._dragElemProxy)

    def _stopDrag(s, evt):
        js.document.removeEventListener("mousemove", s._dragElemProxy)

    def _toggleMenu(s, evt):
        menu = evt.currentTarget.querySelector(".UIElement__menu")
        menu.classList.toggle("shown")

    elemHtml = '''
          <i class="UIElement__caret"
            ><div class="UIElement__menu">
              <div class="UIElement__menu__elem" data-function="delete">
                Delete Widget
              </div>
              <div class="UIElement__menu__elem">Properties</div>
            </div></i
          >'''

    @classmethod
    def _genWidget(cls, evt):
        # event listener function to create instance of widget
        # gets mouse position at time of event and calculates its relative
        # position in the front panel based on bounding rectangle,
        # and then passes those values to the constructor for the
        # initial position of the widget

        # calculate mouse position in the front panel
        fpBounds = js.document.querySelector(
            '[data-page="front-panel"]').getBoundingClientRect()

        initX = evt.clientX-fpBounds.left
        initY = evt.clientY-fpBounds.top

        cls(initX, initY)

    @classmethod
    @abstractmethod
    def _genMenuElem(cls):
        pass


class buttonWidget(UIElement):
    widgets = []
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY):
        # will contain index of instance
        s.index = None

        # will contain DOM element reference of widget
        s.element = None

        # button state
        s.state = False

        # initialize element
        super().__init__(initX, initY)
        s.button = js.document.createElement("div")
        s.button.classList.add("UIbutton")
        s.element.appendChild(s.button)

        # place to store current user button callback
        s.callback = None

        # show widget number
        idTag = js.document.createElement("div")
        idTag.classList.add("UIElement__id")
        idTag.innerText = f"Button {s.index}"
        s.element.appendChild(idTag)

        # add mouse up and down events to button
        s.button.addEventListener("mousedown", create_proxy(s._clickEvent))
        s.button.addEventListener("mouseup", create_proxy(s._releaseEvent))

    def setCallback(s, func):
        # event listeners require an event argument, this adds the
        # arg so the user doesn't have to include it.
        # If I want the user to be able to access the event object
        # I will need to change it
        def newFunc(evt): return func()

        # remove old callback if there is one
        if s.callback:
            s.button.removeEventListener("click", s.callback)

        # If I want user to be able to assign multiple callbacks, will need to keep
        # a list of all assigned callbacks and their corresponding proxies

        # set current callback to one specified by user
        s.callback = create_proxy(newFunc)
        s.button.addEventListener("click", s.callback)

    def _clickEvent(s, evt):
        # changes state to true when button clicked
        s.state = True

    def _releaseEvent(s, evt):
        # changes state to false when button released
        s.state = False

    def isActive(s):
        return s.state

    @classmethod
    def _genMenuElem(cls):
        # generates DOM element that will create an instance of the class
        # when clicked (for add widget menu)

        menuElem = js.document.createElement("div")
        menuElem.innerText = "Button"
        menuElem.classList.add("widget-adder__menu__elem")
        menuElem.addEventListener("click", create_proxy(cls._genWidget))
        return menuElem


class LEDWidget(UIElement):
    widgets = []
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY):
        s.index = None
        s.element = None
        super().__init__(initX, initY)

        # make led
        s.led = js.document.createElement("div")
        s.led.classList.add("UIled")
        s.element.appendChild(s.led)

        # show widget number
        idTag = js.document.createElement("div")
        idTag.classList.add("UIElement__id")
        idTag.innerText = f"LED {s.index}"
        s.element.appendChild(idTag)

    def turnOn(s):
        s.led.classList.add("on")

    def turnOff(s):
        s.led.classList.remove("on")

    def toggle(s):
        s.led.classList.toggle("on")

    def setState(s, state):
        if state == 0:
            s.led.classList.remove("on")
        if state > 0:
            s.led.classList.add("on")

    @classmethod
    def _genMenuElem(cls):
        # generates DOM element that will create an instance of the class
        # when clicked (for add widget menu)

        menuElem = js.document.createElement("div")
        menuElem.innerText = "LED"
        menuElem.classList.add("widget-adder__menu__elem")
        menuElem.addEventListener("click", create_proxy(cls._genWidget))
        return menuElem


# TODO:
# make it so that when a new event listener is assigned, the old one is removed
# make text widget
# make LED widget
