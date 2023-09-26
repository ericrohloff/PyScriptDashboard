import js
from pyodide.ffi import create_proxy
from pyscript import when


class UIElement:
    def __init__(s, initX, initY):
        s.name = None
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
            "[data-function='delete']").addEventListener("click", create_proxy(s._deleteElem))

    def _dragElem(s, evt):
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

    def _deleteElem(s, evt):
        # TODO: once UI class is implemented, have this must also remove the elem from the dict
        if js.window.confirm("Are you sure you want to remove the widget?"):
            s.element.parentNode.removeChild(s.element)

    elemHtml = '''
          <input
            class="UIElement__name"
            type="text"
            placeholder="Enter element name"
          />
          <i class="UIElement__caret"
            ><div class="UIElement__menu">
              <div class="UIElement__menu__elem" data-function="delete">
                Delete Widget
              </div>
              <div class="UIElement__menu__elem">Properties</div>
            </div></i
          >

          <div class="UIbutton"></div>'''
