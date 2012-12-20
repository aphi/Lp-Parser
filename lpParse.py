# TODO: full command line options through optparse or argparse
# clean up/double check of code
# work out elegant error handling
# focus on output objects, and document clearly

# output pulp.LpProblem instance
# need to generate the LpVariable objects, form constraints and objectives, and add them to an LpProblem object
# variables are not directly added to the LpProblem

# ideally we would shift any constraints from the A matrix which only pertain to one variable into the var bounds section

from pyparsing import *
from sys import argv, exit
from lpParse_f import Matrix, multiRemove
import constants

def read(filename):
    # read input lp file
    try:
        fp = open(filename)
        fullDataString = fp.read()
        fp.close()
    except IOError:
        print "Could not find input lp file \"%s\""%argv[1]
        raise IOError


    #name char ranges for objective, constraint or variable
    allNameChars = alphanums + "!\"#$%&()/,.;?@_'`{}|~"
    firstChar = multiRemove(allNameChars, nums + "eE.") #<- can probably use CharsNotIn instead
    name = Word(firstChar, allNameChars, max=255)
    keywords = ["inf", "infinity", "max", "maximum", "maximize", "min", "minimum", "minimize", "s.t.", "st", "bound", "bounds", "bin", "binaries", "binary", "gen",  "general", "end"]
    pyKeyword = MatchFirst(map(CaselessKeyword, keywords))
    validName = ~pyKeyword + name
    validName = validName.setResultsName("name")

    colon = Suppress(oneOf(": ::"))
    plusMinus = oneOf("+ -")
    inf = oneOf("inf infinity", caseless=True)
    number = Word(nums+".")
    sense = oneOf("< <= =< = > >= =>").setResultsName("sense")

    # section tags
    objTagMax = oneOf("max maximum maximize", caseless=True)
    objTagMin = oneOf("min minimum minimize", caseless=True)
    objTag = (objTagMax | objTagMin).setResultsName("objSense")

    constraintsTag = oneOf(["subj to", "subject to", "s.t.", "st"], caseless=True)

    boundsTag = oneOf("bound bounds", caseless=True)
    binTag = oneOf("bin binaries binary", caseless=True)
    genTag = oneOf("gen general", caseless=True)

    endTag = CaselessLiteral("end")

    # coefficient on a variable (includes sign)
    firstVarCoef = Optional(plusMinus, "+") + Optional(number, "1")
    firstVarCoef.setParseAction(lambda tokens: eval("".join(tokens))) #TODO: can't this just be eval(tokens[0] + tokens[1])?

    coef = plusMinus + Optional(number, "1")
    coef.setParseAction(lambda tokens: eval("".join(tokens))) #TODO: can't this just be eval(tokens[0] + tokens[1])?

    # variable (coefficient and name)
    firstVar = Group(firstVarCoef.setResultsName("coef") + validName)
    var = Group(coef.setResultsName("coef") + validName)

    # expression
    varExpr = firstVar + ZeroOrMore(var)
    varExpr = varExpr.setResultsName("varExpr")

    # objective
    objective = objTag + Optional(validName + colon) + varExpr
    objective = objective.setResultsName("objective")

    # constraint rhs
    rhs = Optional(plusMinus, "+") + number
    rhs = rhs.setResultsName("rhs")
    rhs.setParseAction(lambda tokens: eval("".join(tokens)))

    # constraints
    constraint = Group(Optional(validName + colon) + varExpr + sense + rhs)
    constraints = ZeroOrMore(constraint)
    constraints = constraints.setResultsName("constraints")

    # bounds
    signedInf = (plusMinus + inf).setParseAction(lambda tokens:(tokens[0] == "+") * constants.infinity)
    signedNumber = (Optional(plusMinus, "+") + number).setParseAction(lambda tokens: eval("".join(tokens)))  # this is different to previous, because "number" is mandatory not optional
    numberOrInf = (signedNumber | signedInf).setResultsName("numberOrInf")
    ineq = numberOrInf & sense
    sensestmt = Group(Optional(ineq).setResultsName("leftbound") + validName + Optional(ineq).setResultsName("rightbound"))
    freeVar = Group(validName + Literal("free"))

    boundstmt = freeVar | sensestmt 
    bounds = boundsTag + ZeroOrMore(boundstmt).setResultsName("bounds")

    # generals
    generals = genTag + ZeroOrMore(validName).setResultsName("generals") 

    # binaries
    binaries = binTag + ZeroOrMore(validName).setResultsName("binaries")

    varInfo = ZeroOrMore(bounds | generals | binaries)

    grammar = objective + constraintsTag + constraints + varInfo + endTag

    # commenting
    commentStyle = Literal("\\") + restOfLine
    grammar.ignore(commentStyle)

    # parse input string
    parseOutput = grammar.parseString(fullDataString)

    # create generic output Matrix object
    m = Matrix(parseOutput.objective, parseOutput.constraints, parseOutput.bounds, parseOutput.generals, parseOutput.binaries)

    return m

if __name__ == "__main__":
    try:
        argv[1]
    except IndexError:
        print "Usage: $ python lpParse.py <lpfile>"
        exit()
            
    m = read(argv[1])
    print m
