from pyparsing import *

def multiRemove(baseString, removables):
    """ replaces an iterable of strings in removables 
        if removables is a string, each character is removed """
    for r in removables:
        try:
            baseString = baseString.replace(r, "")
        except TypeError:
            raise TypeError, "Removables contains a non-string element"
    return baseString


#name for objective, constraint or variable
allNameChars = alphanums + "!\"#$%&()/,.;?@_'`{}|~"
firstChar = multiRemove(allNameChars, nums + "eE.")

colon = oneOf(": ::")
plusMinus = oneOf("+ -")
number = Word(nums+".")
sense = oneOf("< <= =< = > >= =>")

name = Word(firstChar, allNameChars, max=255)

objOrConstraintDecl = name + colon # use Combine when you want it to as one element

coefAndSign = Optional(plusMinus, "+") + Optional(number, "1")

coefAndSign.setParseAction(lambda tokens: eval("".join(tokens)))

var = Group(coefAndSign.setResultsName("coef") + name.setResultsName("name"))

varExpr = Group(OneOrMore(var)).setResultsName("varExpr")

objective = Optional(objOrConstraintDecl) + varExpr
constraint = Optional(objOrConstraintDecl) + varExpr + sense + number

stmts = constraint | objective

grammar = ZeroOrMore(stmts) + StringEnd()

fp = open("test.lp")
data = fp.readlines()
fp.close()

for l in data:
    token = grammar.parseString(l)
    
    for v in token.varExpr:
        print v.name, v.sign, v.coef
