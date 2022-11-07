from enum import Enum


class MatchType(Enum):
    congruence = 1
    """全匹配(==)"""
    include = 2
    """模糊匹配(in)"""
    regex = 3
    """正则匹配(regex)"""


class IncludeCQCodeError(Exception):
    pass
