import js
from pyodide.ffi import create_proxy
from pyscript import when
import heapq
from abc import ABC, abstractmethod
import asyncio
import cv2
import base64
import numpy as np
from PIL import Image
import io
import copy


class UIElement(ABC):
    # These need to be overridden
    widgets = {}  # abstract
    availableIndexes = []  # abstract
    numWidgets = 0  # abstract

    editable = True

    def __init__(s, initX, initY, genFromClick=True, forcedIdx=None):
        s.xPos = initX
        s.yPos = initY
        s.index = None

        s.element = js.document.createElement("div")

        s.frontPanel = js.document.querySelector("[data-page='front-panel']")
        s.frontPanel.appendChild(s.element)
        s.element.classList.add("UIElement")
        s.element.classList.add("editable")

        # position element under mouse
        s.element.style.left = f"{initX}px"
        s.element.style.top = f"{initY}px"
        s.element.style.transform = "translate(-50%, -50%)"

        s.element.innerHTML = s.elemHtml

        # save drag callback proxies so they can be added and removed
        s._dragElemProxy = create_proxy(s._dragElem)

        # makes it so you can drag element out of button
        if genFromClick:
            js.document.addEventListener("mousemove", s._dragElemProxy)

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
        s._trackNewWidget(forcedIdx)

    def _trackNewWidget(s, forcedIdx):
        # should be called after new widget is created in subclass to properly give
        # the element an ID.
        if forcedIdx != None:
            s.index = forcedIdx
        elif not s.__class__.availableIndexes:
            s.index = s.__class__.numWidgets
        else:
            s.index = heapq.heappop(s.__class__.availableIndexes)
        s.__class__.numWidgets += 1
        s.__class__.widgets[s.index] = s

    def _deleteWidget(s, evt=None, forced=False):
        # event listener for delete button in dropdown menu
        if not forced and not js.window.confirm("Are you sure you want to remove the widget?"):
            return

        # function class can override to add additional destructor steps if necessary
        s._destruct()

        s.element.parentNode.removeChild(s.element)
        s.__class__.numWidgets -= 1
        heapq.heappush(s.__class__.availableIndexes, s.index)
        del s.__class__.widgets[s.index]

    def _dragElem(s, evt):
        # TODO: rework so drag repositioning is based on mouse position instead of movementX/Y for cleaner movement
        evt.preventDefault()
        # event listener for mouse movement to move widget

        dx = evt.movementX
        dy = evt.movementY

        # if transformation would cause element bounding rect to exit front panel, don't allow move.
        # TODO: movement with this is buggy/slow
        dx, dy = s._returnLegalMovement(dx, dy)

        # return if neither direction was legal to avoid unnecessary work
        if not dx and dy:
            return

        elemStyles = js.window.getComputedStyle(s.element)
        # may need to change to regex if more robust parsing needed
        leftStart = (elemStyles.left.rstrip("px"))
        topStart = (elemStyles.top.rstrip("px"))
        topStart = int(float(topStart))
        leftStart = int(float(leftStart))

        s.yPos = topStart+dy
        s.xPos = leftStart+dx

        s.element.style.left = f"{s.xPos}px"
        s.element.style.top = f"{s.yPos}px"

    def _returnLegalMovement(s, dx, dy):
        # checks if given movement to this element is legal
        dy2 = dy
        dx2 = dx

        elemBounds = s.element.getBoundingClientRect()
        fpBounds = js.document.querySelector(
            '[data-page="front-panel"]').getBoundingClientRect()

        # check y movement
        if elemBounds.top + dy < fpBounds.top and dy < 0:
            if elemBounds.top > fpBounds.top:
                dy2 = fpBounds.top - elemBounds.top
            else:
                dy2 = 0

        # allowing movement past bottom for now
        # elif elemBounds.bottom + dy > fpBounds.bottom and dy > 0:
        #     dy2 = 0

        # check x movement
        if elemBounds.left + dx < fpBounds.left and dx < 0:
            if elemBounds.left > fpBounds.left:
                dx2 = fpBounds.left - elemBounds.left
            else:
                dx2 = 0

        elif elemBounds.right + dx > fpBounds.right and dx > 0:
            if elemBounds.right < fpBounds.right:
                dx2 = fpBounds.right - elemBounds.right
            else:
                dx2 = 0

        return dx2, dy2

    def _startDrag(s, evt=None):
        if s.__class__.editable:

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

        evt.preventDefault()

        cls(initX, initY)

    @classmethod
    def enableRunMode(cls):
        # TODO: make this more robust by adding a function for toggling editable instance
        cls.editable = False
        for widget in cls.widgets.values():
            widget.element.classList.remove("editable")

    @classmethod
    def enableEditMode(cls):
        cls.editable = True
        for widget in cls.widgets.values():
            widget.element.classList.add("editable")

    @classmethod
    def saveData(cls):
        # serializes data for all widgets in class and returns dictionary
        data = {}
        widgetData = {}
        for idx, widget in cls.widgets.items():
            widgetData[f"{widget.index}"] = widget.getInstanceData()
        data["widgetData"] = widgetData
        data["indexHeap"] = cls.availableIndexes
        return copy.deepcopy(data)

    def getInstanceData(s):
        # serializes data for instance
        return {
            "xPos": s.xPos,
            "yPos": s.yPos,
        }

    @classmethod
    def loadData(cls, data):
        print(f"loading {cls.__name__}")
        # print(data["indexHeap"])
        cls.clearClass()
        # print(data["indexHeap"])
        cls.availableIndexes = copy.deepcopy(data["indexHeap"])
        # print(f"aidx:{cls.availableIndexes}")
        # print("___")
        for key, value in data["widgetData"].items():
            idx = int(key)
            cls.instantiateFromData(value, idx)

    @classmethod
    def instantiateFromData(cls, data, idx):
        initX = data["xPos"]
        initY = data["yPos"]
        return cls(initX, initY, genFromClick=False, forcedIdx=idx)

    @classmethod
    def clearClass(cls):
        for idx in list(cls.widgets.keys()).copy():
            cls.widgets[idx]._deleteWidget(forced=True)
        cls.numWidgets = 0
        cls.availableIndexes = []
        cls.widgets = {}

    @classmethod
    def _genMenuElem(cls):
        pass

    # function subclass can override to implement proper destruction
    def _destruct(s):
        pass


class buttonWidget(UIElement):
    widgets = {}
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY, genFromClick=True, forcedIdx=None):
        # will contain index of instance
        s.index = None

        # will contain DOM element reference of widget
        s.element = None

        # button state
        s.state = False

        # initialize element
        super().__init__(initX, initY, genFromClick, forcedIdx)
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
        menuElem.addEventListener("mousedown", create_proxy(cls._genWidget))
        return menuElem


class LEDWidget(UIElement):
    widgets = {}
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY, genFromClick=True, forcedIdx=None):
        s.index = None
        s.element = None
        s.isOn = False
        super().__init__(initX, initY, genFromClick, forcedIdx)

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
        s.isOn = True

    def turnOff(s):
        s.led.classList.remove("on")
        s.isOn = False

    def toggle(s):
        s.led.classList.toggle("on")
        s.isOn = not s.isOn

    def setState(s, state):
        if state == 0:
            s.turnOff()
        if state > 0:
            s.turnOn()

    def isOn(s):
        return s.isOn

    @classmethod
    def _genMenuElem(cls):
        # generates DOM element that will create an instance of the class
        # when clicked (for add widget menu)

        menuElem = js.document.createElement("div")
        menuElem.innerText = "LED"
        menuElem.classList.add("widget-adder__menu__elem")
        menuElem.addEventListener("mousedown", create_proxy(cls._genWidget))
        return menuElem


class cameraWidget(UIElement):
    widgets = {}
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY, genFromClick=True, forcedIdx=None):
        s.index = None
        s.element = None
        s.stream = None
        s.lastSnap = None

        super().__init__(initX, initY, genFromClick, forcedIdx)

        # make start camera button
        s.startButton = js.document.createElement("button")
        s.startButton.classList.add("UIcamera__startbutton")
        s.startButton.innerText = "Start Camera"
        s.element.appendChild(s.startButton)

        # make snap button
        s.snapButton = js.document.createElement("button")
        s.snapButton.classList.add("UIcamera__startbutton")
        s.snapButton.innerText = "Snap"
        s.element.appendChild(s.snapButton)

        # make camera
        s.camera = js.document.createElement("video")
        s.camera.classList.add("UIcamera")
        s.camera.autoplay = True
        s.element.appendChild(s.camera)

        # tie start callback
        s.startButton.addEventListener("click", create_proxy(s._cameraStart))
        s.snapButton.addEventListener("click", create_proxy(s.snap))

        # show widget number
        idTag = js.document.createElement("div")
        idTag.classList.add("UIElement__id")
        idTag.innerText = f"Camera {s.index}"
        s.element.appendChild(idTag)

        # create hidden canvas, this will be used to store the full resolution image
        # TODO: figure out a better way to do this
        s.canvas = js.document.createElement("canvas")
        s.element.appendChild(s.canvas)
        s.ctx = s.canvas.getContext("2d")
        s.canvas.style.width = "267px"
        s.canvas.style.height = "200px"

    def snap(s, evt=None):
        height = s.camera.videoHeight
        width = s.camera.videoWidth
        # grab current frame
        s.ctx.drawImage(s.camera, 0, 0, width,
                        height)

        imageDataURL = s.canvas.toDataURL('image/jpeg')
        b64String = imageDataURL.split("base64,")[1]
        rawPIL = Image.open(io.BytesIO(base64.b64decode(b64String)))
        s.lastSnap = rawPIL

        return s.lastSnap

    async def _cameraStart(s, evt):
        media = js.Object.new()
        media.audio = False
        media.video = True
        s.stream = await js.navigator.mediaDevices.getUserMedia(media)
        s.camera.srcObject = s.stream

        while s.camera.videoWidth == 0:
            await asyncio.sleep(0.1)

        # set canvas resolution after video starts
        s.canvas.width = s.camera.videoWidth
        s.canvas.height = s.camera.videoHeight

    def _destruct(s):
        if s.stream:
            s.stream.getTracks()[0].stop()

    @classmethod
    def _genMenuElem(cls):
        # generates DOM element that will create an instance of the class
        # when clicked (for add widget menu)

        menuElem = js.document.createElement("div")
        menuElem.innerText = "Camera"
        menuElem.classList.add("widget-adder__menu__elem")
        menuElem.addEventListener("mousedown", create_proxy(cls._genWidget))
        return menuElem


class canvasWidget(UIElement):
    widgets = {}
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY, genFromClick=True, forcedIdx=None):
        s.index = None
        s.element = None

        super().__init__(initX, initY, genFromClick, forcedIdx)

        # make canvas
        s.canvas = js.document.createElement("canvas")
        s.canvas.classList.add("UIcanvas")
        s.element.appendChild(s.canvas)

        s.ctx = s.canvas.getContext("2d")
        s._scaleContext()

        # show widget number
        idTag = js.document.createElement("div")
        idTag.classList.add("UIElement__id")
        idTag.innerText = f"Canvas {s.index}"
        s.element.appendChild(idTag)

    def renderImage(s, rgba):
        # TODO: force rgba to be numpy array with 3 dims and the 3rd being a size of 4

        # convert passed numpy array into expected 1d format
        dims = rgba.shape
        height = dims[0]
        width = dims[1]
        channels = dims[2]

        dataList = [0]*rgba.size
        idx = 0
        for i in range(height):
            for j in range(width):
                for k in range(channels):
                    dataList[idx] = rgba[i][j][k]
                    idx += 1

        # resize canvas resolution
        s.canvas.width = width
        s.canvas.height = height

        # change canvas aspect ratio
        s.canvas.style.aspectRatio = f"{width}/{height}"
        js.console.log(width)
        js.console.log(height)
        js.console.log(len(dataList))
        imgData = s.ctx.createImageData(width, height)
        for i in range(len(dataList)):
            imgData.data[i] = dataList[i]
        print("here")
        s.ctx.putImageData(imgData, 0, 0)

    def _scaleContext(s):
        # needed if canvas is resized to make x and y axis equivalently scaled
        s.ctx.scale(s.canvas.width/s.canvas.offsetWidth,
                    s.canvas.height/s.canvas.offsetHeight)

    @classmethod
    def _genMenuElem(cls):
        # generates DOM element that will create an instance of the class
        # when clicked (for add widget menu)

        menuElem = js.document.createElement("div")
        menuElem.innerText = "Canvas"
        menuElem.classList.add("widget-adder__menu__elem")
        menuElem.addEventListener("mousedown", create_proxy(cls._genWidget))
        return menuElem


class imageFrameWidget(UIElement):
    widgets = {}
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY, genFromClick=True, forcedIdx=None):
        s.index = None
        s.element = None

        super().__init__(initX, initY, genFromClick, forcedIdx)

        # make canvas
        s.img = js.document.createElement("img")
        s.img.classList.add("UIimage")
        s.element.appendChild(s.img)

        # show widget number
        idTag = js.document.createElement("div")
        idTag.classList.add("UIElement__id")
        idTag.innerText = f"Image {s.index}"
        s.element.appendChild(idTag)

    def displayPil(s, PILimage):
        width, height = PILimage.size
        imgByteArr = io.BytesIO()
        PILimage.save(imgByteArr, format='png')
        imgByteArr = imgByteArr.getvalue()
        data = base64.b64encode(imgByteArr).decode('utf-8')
        src = f"data:image/png;base64,{data}"
        s.img.setAttribute("src", src)
        s.img.style.width = f"{width/height*s.img.clientHeight}px"

    def displayCv2(s, cv2Image):
        PILimage = Image.fromarray(cv2.cvtColor(cv2Image, cv2.COLOR_BGRA2RGBA))
        s.displayPil(PILimage)

    @classmethod
    def _genMenuElem(cls):
        # generates DOM element that will create an instance of the class
        # when clicked (for add widget menu)

        menuElem = js.document.createElement("div")
        menuElem.innerText = "Image Frame"
        menuElem.classList.add("widget-adder__menu__elem")
        menuElem.addEventListener("mousedown", create_proxy(cls._genWidget))
        return menuElem


# TODO:
# make saving text widget work (doesnt save contents)
# also issues editing text
# make text widgets not generate in run mode

class textWidget(UIElement):
    widgets = {}
    availableIndexes = []
    numWidgets = 0

    def __init__(s, initX, initY):
        s.element = None

        s.xPos = initX
        s.yPos = initY
        s.index = None

        s.element = js.document.createElement("div")

        s.frontPanel = js.document.querySelector("[data-page='front-panel']")
        s.frontPanel.appendChild(s.element)
        s.element.classList.add("UIElement")
        s.element.classList.add("editable")

        # position element under mouse
        s.element.style.left = f"{initX}px"
        s.element.style.top = f"{initY}px"
        s.element.style.transform = "translate(-50%, -50%)"

        # save drag callback proxies so they can be added and removed
        s._dragElemProxy = create_proxy(s._dragElem)

        # add drag event listeners
        s.element.addEventListener("mousedown", create_proxy(s._startDrag))
        js.document.addEventListener("mouseup", create_proxy(s._stopDrag))

        # track widget in class attributes
        s._trackNewWidget(None)

        # make text box
        s.textBox = js.document.createElement('input')
        s.textBox.setAttribute('type', 'text')
        s.element.appendChild(s.textBox)
        s.textBox.focus()

        s.textBox.addEventListener('blur', create_proxy(s._checkEmpty))

    def _checkEmpty(s, evt):
        if not s.textBox.value.strip():
            s._deleteWidget(forced=True)

    # needed to override this as this class doesn't have the genFromClick
    @classmethod
    def instantiateFromData(cls, data, idx):
        initX = data["xPos"]
        initY = data["yPos"]
        return cls(initX, initY, forcedIdx=idx)
