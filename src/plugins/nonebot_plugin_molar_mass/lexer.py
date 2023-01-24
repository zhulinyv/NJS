from rply import LexerGenerator


lg = LexerGenerator()

lg.ignore(r'\s+')
lg.add('INTEGER', r'\d+')
lg.add('ELEMENT', '[A-Z][a-z]?')
lg.add('OPEN_PARENS', r'\(')
lg.add('CLOSE_PARENS', r'\)')
lg.add('ADD', r'\+')

lexer = lg.build()
