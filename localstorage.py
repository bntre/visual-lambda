# Exchange with localStorage.
# Works on web platform only.

# https://github.com/pygame-web/pygame-web.github.io/blob/main/wiki/pygbag-code/README.md

# Add this to index.html:
r"""
    // localStorage exchange
    function setStorageValue(name, newValue, separator = undefined) {
        let key = "storage_" + name;
        let value = undefined;
        if (separator) {
            value = window.localStorage.getItem(key);
            if (value) {
                value += separator + newValue;
            } else {
                value = newValue;
            }
        } else {
            value = newValue;
        }
        window.localStorage.setItem(key, value);
    }
    
    function addItem(expression) {
        setStorageValue("addItem", expression, "|");
    }
    function saveWorkspace(workspaceName) {
        setStorageValue("saveWorkspace", workspaceName);
    }
    function loadWorkspace(workspaceName) {
        setStorageValue("loadWorkspace", workspaceName);
    }
    function help() {
        console.log("addItem(expression) - add an item by expression, e.g. addItem('\\x. x x')");
        console.log("saveWorkspace(workspaceName) - save current workspace to localStorage, e.g. saveWorkspace('combinators3')");
        console.log("loadWorkspace(workspaceName) - load a workspace from localStorage, e.g. loadWorkspace('combinators3')");
    }
"""


import config


if config.IS_WEB_PLATFORM:
    from platform import window

else:
    raise Exception("LocalStorage only available for Web")


def handle_storage(name, proc, separator = None):
    key = "storage_%s" % name
    storageValue = window.localStorage.getItem(key)
    
    if not storageValue: return
    
    window.localStorage.setItem(key, "")
    
    values = separator and storageValue.split(separator) or (storageValue,)
    for v in values:
        proc(v)


def save_value(key, value):
    window.localStorage.setItem(key, value)
    
def load_value(key):
    return window.localStorage.getItem(key)
