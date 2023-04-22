import json

from typing import Union
from pathlib import Path

from rply import ParserGenerator
from rply.token import BaseBox


ELEMENTS: dict[str, Union[int, float]] = json.loads(
    (Path(__file__).parent / 'elements.json').read_text('utf8')
)


class Expr(BaseBox):
    def eval(self) -> Union[int, float]:
        raise NotImplementedError()


class IntegerExpr(Expr):
    def __init__(self, expr: Expr, count: int):
        self.expr = expr
        self.val = count

    def eval(self) -> Union[int, float]:
        return self.expr.eval() * self.val


class Element(Expr):
    def __init__(self, ele: str):
        self.ele = ele

    def eval(self) -> Union[int, float]:
        if self.ele not in ELEMENTS:
            raise NameError('Cannot find element ' + self.ele)
        return ELEMENTS[self.ele]


class AddExpr(Expr):
    def __init__(self, left: Expr, right: Expr):
        self.left = left
        self.right = right

    def eval(self) -> Union[int, float]:
        return self.left.eval() + self.right.eval()


pg = ParserGenerator([
    'INTEGER', 'ELEMENT', 'OPEN_PARENS', 'CLOSE_PARENS', 'ADD'
], precedence=[
    ('left', ['ADD'])
])


@pg.production('final_expr : final_expr ADD final_expr')
def _(p):
    return AddExpr(p[0], p[2])


@pg.production('final_expr : INTEGER expr')
def _(p):
    return IntegerExpr(p[1], int(p[0].getstr()))


@pg.production('final_expr : expr')
@pg.production('expr : ele')
@pg.production('expr : paren')
def _(p):
    return p[0]


@pg.production('expr : ele expr')
@pg.production('expr : paren expr')
def _(p):
    return AddExpr(p[0], p[1])


@pg.production('paren : OPEN_PARENS expr CLOSE_PARENS')
def _(p):
    return p[1]


@pg.production('paren : OPEN_PARENS expr CLOSE_PARENS INTEGER')
def _(p):
    return IntegerExpr(p[1], int(p[3].getstr()))


@pg.production('ele : ELEMENT')
def _(p):
    return Element(p[0].getstr())


@pg.production('ele : ELEMENT INTEGER')
def _(p):
    return IntegerExpr(Element(p[0].getstr()), int(p[1].getstr()))


@pg.error
def _(token):
    raise ValueError(f'{token.gettokentype()} was not expected.')


parser = pg.build()
