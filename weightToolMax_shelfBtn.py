import importlib
path = r"YOUR PATH HERE"
if path not in sys.path:
    sys.path.append(path)
from UI import weightToolMax_UI as UI
importlib.reload(UI)
UI.openWindow()
