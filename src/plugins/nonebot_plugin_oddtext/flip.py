flip_table = {
    "a": "\u0250",
    "b": "q",
    "c": "\u0254",
    "d": "p",
    "e": "\u01DD",
    "f": "\u025F",
    "g": "\u0183",
    "h": "\u0265",
    "i": "\u0131",
    "j": "\u027E",
    "k": "\u029E",
    "l": "\u0283",
    "m": "\u026F",
    "n": "u",
    "r": "\u0279",
    "t": "\u0287",
    "v": "\u028C",
    "w": "\u028D",
    "y": "\u028E",
    ".": "\u02D9",
    "[": "]",
    "(": ")",
    "{": "}",
    "?": "\u00BF",
    "!": "\u00A1",
    "'": ",",
    "<": ">",
    "_": "\u203E",
    ";": "\u061B",
    "\u203F": "\u2040",
    "\u2045": "\u2046",
    "\u2234": "\u2235",
    "\r": "\n",
}


flip_table_new = flip_table.copy()
for i in flip_table.keys():
    flip_table_new[flip_table[i]] = i
flip_table = flip_table_new
