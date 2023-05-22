
# Calling input() in separate thread to avoid freezing.
# Not used on web platform.

import threading


class Input:
    def __init__(self, callback):
        self.callback = callback
        self.result   = None  # None until the text got


_inputs = []  # Input objects
_inputInProgress = False
_inputGot = False


def _consoleProc(prompt):  # console thread
    global _inputs, _inputInProgress, _inputGot
    _inputInProgress = True
    _inputs[-1].result = input(prompt)  # blocking
    _inputInProgress = False
    _inputGot = True



def requestInput( prompt, callback ):  # call in main thread
    if _inputInProgress:
        return False        # Sorry! Previous input is not finished.

    global _inputs

    _inputs.append(Input(callback))

    threading.Thread(
        name = 'Console input',
        target = _consoleProc,
        args = (prompt,)
    ).start()
    
    return True


def checkInputs():  # call in main thread
    global _inputGot, _inputs
    
    if not _inputGot: return

    def check(i):
        if i.result is None:
            return True  # keep waiting
        else:
            i.callback(i.result)
            return False  # not needed anymore

    _inputs = list(filter(check, _inputs))
    _inputGot = False


def isWaiting():  # call in main thread
    return len(_inputs) > 0

