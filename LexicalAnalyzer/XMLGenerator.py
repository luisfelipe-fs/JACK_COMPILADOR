from JackTokenizer import JackTokenizer
from Token import Token

REPLACEMENTS = {'<': '&lt;', '>': '&gt;', '"': '&quot;', '&': '&amp;'}

tknz = JackTokenizer("Main.jack")
tknz.advance()
with open("Main.xml", "w+") as f:
    f.write("<tokens>\n")
    while tknz.hasMoreTokens():
        tokenClass = tknz.tokenType()
        f.write("<"+tokenClass+">")
        # fix some words for proper xml visualization
        currentToken = tknz.getToken()
        if tokenClass != Token.TK_STRING:
            try:
                currentToken = REPLACEMENTS[currentToken]
            except:
                pass
            f.write(currentToken)
        else:
            f.write(currentToken[1:-1])
        f.write("</"+tokenClass+">\n")
        tknz.advance()
    f.write("</tokens>\n")
