"""
some basic functions to support lpParse.py
"""

class Matrix:
    """ output matrix class """
    
    class Objective:
        def __init__(self, expression, sense, name):
            self.name = name
            self.sense = sense # TODO: urgently need to sort out what we mean by this. there is obj dir, and constraint type which can't both be called sense
            self.expression = expression # - a dict with variable names as keys, and coefficients as values

    class Constraint:
        def __init__(self, expression, sense, rhs, name):
            self.name = name
            self.sense = sense
            self.rhs = rhs
            self.expression = expression # - a dict with variable names as keys, and coefficients as values
    
    class Variable:
        def __init__(self, bounds, category, name):
            self.name = name
            self.bounds = bounds # a tuple (lb, ub)
            self.category = category

    def __init__(self):
        self.objective = Objective(name, sense, expression)
        
        self.constraints = [Constraint(expression, sense, rhs, name) for i in i]

        self.variables = [Variable(bounds, category, name)]

# TODO: can use those Matrix.LE, Matrix.GE or lpParse.LEQ etc notation for constants


def multiRemove(baseString, removables):
    """ replaces an iterable of strings in removables 
        if removables is a string, each character is removed """
    for r in removables:
        try:
            baseString = baseString.replace(r, "")
        except TypeError:
            raise TypeError, "Removables contains a non-string element"
    return baseString
