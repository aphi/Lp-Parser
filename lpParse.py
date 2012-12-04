# TODO: full command line options through optparse or argparse
# clean up/double check of code
# work out elegant error handling
# focus on output objects, and document clearly

# ideally we would shift any constraints from the A matrix which only pertain to one variable into the var bounds section

from pyparsing import *
from sys import argv

from ordereddict import OrderedDict as odict
from lpParse_f import Matrix, multiRemove, setBounds

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
objTag = objTagMax | objTagMin
objTag.setResultsName("objSense")

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
objective = Optional(validName + colon) + varExpr
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
numberOrInf = number | Combine(plusMinus + inf)
sensestmt = Group(Optional(numberOrInf + sense) + validName + Optional(sense + numberOrInf))
freeVar = Group(validName + Literal("free"))

boundstmt = freeVar | sensestmt 
bounds = boundsTag + ZeroOrMore(boundstmt).setResultsName("bounds")

# generals
generals = genTag + ZeroOrMore(validName).setResultsName("generals") 

# binaries
binaries = binTag + ZeroOrMore(validName).setResultsName("binaries")

varInfo = ZeroOrMore(bounds | generals | binaries)

grammar = objTag + objective + constraintsTag + constraints + varInfo + endTag

# commenting
commentStyle = Literal("\\") + restOfLine
grammar.ignore(commentStyle)

fp = open(argv[1])
fullDataString = fp.read()
fp.close()

full = grammar.parseString(fullDataString)

#print full

outputObjective = {}

o = full.objective
print "Objective: %s"%o.objSense
print o.name, o.varExpr
outputObjective["sense"] = o.objSense
outputObjective["name"] = o.name
outputObjective["expression"] = {}
for v in o.varExpr:
    outputObjective["expression"][v.name] = v.coef 

outputConstraints = {}

senseLiterals = {"<":"le", "<=":"le", "=<":"le", "=":"eq", ">":"ge", ">=":"ge", "=>":"ge"}

print "\nConstraints"
for c in full.constraints:
    outputConstraints[c.name] = {}
    outputConstraints[c.name]["name"] = c.name
    outputConstraints[c.name]["rhs"] = c.rhs
    outputConstraints[c.name]["sense"] = senseLiterals[sense]
    outputConstraints[c.name]["expression"] = {}
    for v in c.varExpr:
        outputConstraints[c.name]["expression"][v.name] = v.coef

outputVarRanges = {}
print "\nBounds"
for b in full.bounds:
    if len(b) == 2: # free var
        outputVarRanges[b[0]] = {"lb":None, "ub":None}
        
    elif len(b) == 3: # one sided ineq

        setBounds(outputVarRanges, b)
        sense = senseLiterals[b[1]]

        if hasattr(b[0], "name"):
            if sense == "le": # v <= b[2]
                outputVarRanges[b[0]] = {"lb":None, "ub":b[2]}
            elif sense == "ge": # v >= b[2]
                outputVarRanges[b[0]] = {"lb":b[2], "ub":None}
            else: # v == b[2]
                outputVarRanges[b[0]] = {"lb":b[2], "ub":b[2]}

        elif hasattr(b[2], "name"):
            if sense == "le": # b[0] <= v
                outputVarRanges[b[2]] = {"lb":b[0], "ub":None}
            elif sense == "ge": # b[0] >= v
                outputVarRanges[b[2]] = {"lb":None, "ub":b[0]}
            else: # b[0] == v
                outputVarRanges[b[2]] = {"lb":b[0], "ub":b[0]}
        
    
    elif len(b) == 5: # two sided ineq
        
        outputVarRanges[b[2]] = {"lb": , "ub":}


print "\nGenerals"
for g in full.generals:
    print g

print "\nBinaries"
for b in full.binaries:
    print b

