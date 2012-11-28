# TODO: full command line options through optparse or argparse
# clean up/double check of code
# focus on output objects, and document clearly

from pyparsing import *
from sys import argv

from lpParse_f import Matrix, multiRemove

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
firstVarCoef.setParseAction(lambda tokens: eval("".join(tokens)))

coef = plusMinus + Optional(number, "1")
coef.setParseAction(lambda tokens: eval("".join(tokens)))

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

o = full.objective
print "Objective: %s"%o.objSense
print o.name, o.varExpr

print "\nConstraints"
for c in full.constraints:
    print c.name, c.varExpr, c.sense, c.rhs

print "\nBounds"
for b in full.bounds:
    print b

print "\nGenerals"
for g in full.generals:
    print g

print "\nBinaries"
for b in full.binaries:
    print b



