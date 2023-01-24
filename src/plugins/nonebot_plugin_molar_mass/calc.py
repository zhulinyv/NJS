from .lexer import lexer
from .parser import parser


class CalcException(Exception):
    pass


def calc_molar_mass(chemical: str) -> str:
    """
    Calculates the molar mass of given chemical.
    :raise CalcException: if fails to calculate.
    :param chemical: the chemical to calculate.
    :return: the molar mass in formatted string.
    """

    try:
        return '{:g}'.format(parser.parse(lexer.lex(chemical)).eval())
    except Exception as e:
        raise CalcException() from e
