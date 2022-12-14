"""
    calc2tex.calc_unit
    ~~~~~~~~~~~~~~~~~~

    Processes a unit into valid LaTeX.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


from .helpers import search_char, is_float
from .settings import units


def subunit_to_tex(split: str) -> str:
    """
    Converts part of a unit from the symbol to the command of the siunitx-package

    Parameters
    ----------
    split : str
        Part of the inputed unit, one symbol or a number.

    Returns
    -------
    str
        The command from the siunitx-package representing the symbol.

    """
    length = len(split)
    if is_float(split):
        return "\\tothe{" + split + "}"
    
    if length == 1:
        return units["singleun"][split]
    elif length == 2:
        try:
            return units["doubleun"][split]
        except:
            pass
        return units["singlepre"][split[0]] + units["singleun"][split[1]]
    elif length == 3:
        try:
            return units["tribleun"][split]
        except:
            pass
        try: 
            return units["doublepre"][split[0:2]] + units["singleun"][split[2]]
        except:
            pass
        return units["singlepre"][split[0]] + units["doubleun"][split[1:3]]
    elif length == 4:
        try:
            return units["singlepre"][split[0]] + units["tribleun"][split[1:4]]
        except:
            pass
        return units["doublepre"][split[0:2]] + units["doubleun"][split[2:4]]
    elif length == 5:
        return units["doublepre"][split[0:2]] + units["tribleun"][split[2:5]]

    
    return "??"
#TODO print warning


def unit_to_tex(unit: str) -> str:
    """
    Converts the unit from the input-file to a string, that can be used by the siunitx-package.

    Parameters
    ----------
    unit : str
        The complete unit, as extracted from the file.

    Returns
    -------
    str
        A string, that can be inputed in LaTeX.

    """
    if unit == "-" or unit == "":
        return ""
    
    truth = True
    index_last = 0
    tex_unit = ""
    
    while truth:    #TODO while True
        index_next = search_char(unit, index_last, ("/", "*"))
        
        if index_next - index_last != 0:
            tex_unit += subunit_to_tex(unit[index_last:index_next])
        if index_next == len(unit):
            break
        if unit[index_next] == "/":
            tex_unit += "\\per"
        index_last = index_next + 1
            
    return tex_unit

