"""
some basic functions to support lpParse.py
"""

def multiRemove(baseString, removables):
    """ replaces an iterable of strings in removables 
        if removables is a string, each character is removed """
    for r in removables:
        try:
            baseString = baseString.replace(r, "")
        except TypeError:
            raise TypeError, "Removables contains a non-string element"
    return baseString
