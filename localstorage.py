# Exchange with localStorage.
# Works on web platform only.

# https://github.com/pygame-web/pygame-web.github.io/blob/main/wiki/pygbag-code/README.md

# See the writing to localStorage in pygbag_index_html.tmpl


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
