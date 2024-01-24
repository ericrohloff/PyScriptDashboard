import js
from pyodide.ffi import create_proxy
from widgets import *
from UITracker import *

# was originally going to initialize this class on page load and
# have it track each new element created and store it in a dictionary
# but I think it might be more efficient to have the class just
# retrieve the element by seraching the DOM


class pyViewUI:
    def __init__(s):
        pass

# funcitonality I want:
# retrieve widget
