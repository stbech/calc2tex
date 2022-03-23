"""
    calc2tex.calc_formula
    ~~~~~~~~~~~~~~~~~~~~~

    Processes a formula into valid LaTeX and
    calculates its value.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


from .helpers import is_float, search_char, search_bracket, exponential_rounding
from .settings import mult_sign #ersetze mit settings.mult_sign
from calc2tex import settings
import re
#Imports for evaluating formula:
import numpy as np
from calc2tex import trigo

#TODO alles in settings
tex_commands = ("e", "pi", "sin", "cos", "tan", "sqrt", "arccos", "arcsin", "arctan", "arcsinh", "arccosh", "arctanh", "sinh", "cosh", "tanh")
trigo_list = ("sinD", "cosD", "tanD", "arccosD", "arcsinD", "arctanD", "sinG", "cosG", "tanG", "arccosG", "arcsinG", "arctanG")
funct_indicators = {"?(": ("?(", ")"), "~(": ("?{", "}"), "$(": ("?[", "]"), "°(": ("?´", "`")}
chars_in_formula = ("/", "*", "(", ")", "+", "-", "%", ",") #are not allowed in the dictionary-keys
search_minmax = re.compile(r"(^|[ ,*/%+()-]+)(min\()|(max\()")  #a pattern that recognizes min- or max-functions in a string

#TODO x**x**x wird in Python als x**(x**x) behandelt -> Darstellung in Latex


def split_mult(string: str) -> str:
    """
    Splits the string on the highest order factors und passes them again into the split_sum-function.

    Parameters
    ----------
    string : str
        A formula, which is preprocessed by split_sum and split_quo.

    Returns
    -------
    str
        The input with the single factors processed.

    """
    index_last = 0
    back = ""
    
    while True:
        index_start = search_char(string, index_last, ("("))
        if index_start == len(string):
            back += string[index_last:index_start]
            break
        
        index_next = search_bracket(string, index_start, 1)
        
        back += "".join((string[index_last:index_start+1], split_sum(string[index_start+1:index_next]), string[index_next]))
        
        index_last = index_next + 1
    
    return back



def split_quo(string: str) -> str:
    """
    Converts fractions.

    Parameters
    ----------
    string : str
        The formula preprocessed by split_funct, split_expo and split_sum.

    Returns
    -------
    str
        Processed formula.

    """
    #TODO ?/?/? berücksichtigen -> \frac{?}{?*?}
    index_last, index_start = 0, 0
    back = ""
    
    if string[0] == "+" or string[0] == "-":
        index_last = 1
        back += string[0]
        
    while True:
        while True:
            index_next = search_char(string, index_start, ("/"))
            index_start = index_next + 1
            if string.count("(", 0, index_next) - string.count(")", 0, index_next) == 0:
                break
            
        if index_next == len(string):
            back += split_mult(string[index_last:])
            break
    
        if string[index_next+1] == "/":
            intdiv = True
            index_start += 1
            start, end = index_next - 1, index_next + 2
        else:
            intdiv = False
            start, end = index_next - 1, index_next + 1
        
        if string[start] == ")":
            start = search_bracket(string, start, -1)
            numerator = split_sum(string[start+1:index_next-1])
        else:
            numerator = string[start]
        
        if string[end] == "(":
            end = search_bracket(string, end, 1)
            if intdiv:
                denominator = split_sum(string[index_next+3:end])
            else:
                denominator = split_sum(string[index_next+2:end])
        else:
            denominator = string[end]
        
        before = split_mult(string[index_last:start])
        if intdiv:
            back += "".join((before,"\\left\\lfloor\\frac{", numerator, "}{", denominator, "}\\right\\rfloor "))
        else:
            back += "".join((before,"\\frac{", numerator, "}{", denominator, "}"))
        index_last = end + 1
      
    return back



def split_sum(string: str) -> str:
    """
    Splits the formula on single summands and processes one a time.

    Parameters
    ----------
    string : str
        The formula preprocessed by split_funct and split_expo.

    Returns
    -------
    str
        Processed formula.

    """
    if len(string) == 0:
        return string
    #TODO muss index_last auf 1 gesetzt werden, immer auf 1 -> if bedingung in schleife weg
    if string[0] == "+" or string[0] == "-":
        index_last, index_start = 1, 1
    else:
        index_last, index_start = 0, 0
    back = ""
    
    while True:
        index_next = search_char(string, index_start, ("+", "-"))
        if string.count("(", 0, index_next) - string.count(")", 0, index_next) == 0:
            if index_last == 0:
                back += split_quo(string[index_last:index_next])
            else:
                back += split_quo(string[index_last-1:index_next])
            index_last = index_next + 1
        
        if index_next == len(string):
            break
        
        index_start = index_next + 1
       
    return back 



def split_expo(string: str) -> str:
    """
    Takes a string and processes all exponents.

    Parameters
    ----------
    string : str
        Formula preprocessed by split_funct.

    Returns
    -------
    str
        Processed formula.

    """
    index_last = 0
    expos = []
    
    while True:
        index_next = search_char(string, index_last, ("**",))
        if index_next == len(string):
            break
        
        start, end = index_next - 1, index_next + 2
        
        if string[start] == ")":
            start = search_bracket(string, start, -1)
            base = "(" + split_sum(string[start+1:index_next-1]) + ")"
        else:
            base = string[start]
            
        if string[end] == "(":
            end = search_bracket(string, end, 1)
            if "**" in string[index_next+3:end]:
                power = split_expo(string[index_next+3:end])
            else:
                power = split_sum(string[index_next+3:end])
        else:
            power = string[end]
        
        expo_in_base = string.count("§", start, index_next)
        
        expos.insert(len(expos)- expo_in_base, "".join((base, "^{", power, "}")))
        string = string.replace(string[start:end+1], "§", 1)
        
        index_last = start
    
    back = split_sum(string)
    
    for expo in expos:
        back = back.replace("§", expo, 1)
        
    return back



def split_comma(string: str) -> str:
    """
    Splits a function at the commas and processes the parts. 

    Parameters
    ----------
    string : str
        The argument of a function.

    Returns
    -------
    str
        The joined and processed arguments.

    """
    index_last, index_start = 0, 0
    args = []
    
    while True:
        index_next = search_char(string, index_start, (","))
        if string.count("(", index_next) == string.count(")", index_next):
            args.append(string[index_last:index_next])
            index_last = index_next + 1
            
        if index_next == len(string):
            break
        
        index_start = index_next + 1
    
    for i, arg in enumerate(args):
        args[i] = split_funct(arg)
            
    return "\\\\\n".join(args)



def split_funct(string: str) -> str:
    """
    Searches for functions inside string and separatly converts them.

    Parameters
    ----------
    string : str
        The unprocessed formula.

    Returns
    -------
    str
        Nearly to LaTeX converted formula.

    """
    functions = []
    index_last = 0
    
    while True:
        index_start = search_char(string, index_last, funct_indicators.keys())
        
        if index_start >= len(string):
            break
        
        index_next = search_bracket(string, index_start+1, 1)
            
        for key, item in funct_indicators.items():
            if key[0] == string[index_start]:
                functions.append("".join((item[0], split_comma(string[index_start+2:index_next]), item[1])))
                break
                
        string = string.replace(string[index_start:index_next+1], "!", 1)
        index_last = index_start
    
    
    back = split_expo(string)
    
    for funct in functions:
        back = back.replace("!", funct, 1)
    
    return back



def find_vars(formula: str) -> (str, list):
    """
    Replaces all variables, numbers, commands inside formula by single chars, mainly question marks. 

    Parameters
    ----------
    formula : str
        The non-processed formula from the txt-file.

    Returns
    -------
    short_formula : str
        The shortened formula.
    var_list : list
        The list of extracted variables.

    """
    index_last = 0
    short_formula = ""
    var_list = []
    #TODO TEST strip trailing and leading whitespace before appending?
    while True:
        index_next = search_char(formula, index_last, chars_in_formula)
        
        if index_next - index_last != 0:
            var = formula[index_last:index_next]
            var_list.append(var.strip())
            if var == "sqrt":
                short_formula += "~"
            elif var == "abs":
                short_formula += "$"
            elif var in ("min", "max"):
                short_formula += "°"
            else:
                short_formula += "?"
                
        if index_next == len(formula):
            break
        
        short_formula += formula[index_next]
        index_last = index_next + 1
    
    return short_formula, var_list



def formula_to_tex(formula: str) -> str:
    """
    Mainly for calling a deeper level to convert the shortened formula to LaTeX and some post-processing.

    Parameters
    ----------
    formula : str
        The shortened formula, where variables are represented as question marks.

    Returns
    -------
    str
        The processed formula.

    """
    back = split_funct(formula)
    
    back = back.replace("*", mult_sign + " ")
    back = back.replace("(", "\\left(")
    back = back.replace(")", "\\right)")
    back = back.replace("[", "\\left|")
    back = back.replace("]", "\\right|")
    back = back.replace("´", "\\begin{Bmatrix}")
    back = back.replace("`", "\\end{Bmatrix}")
    back = back.replace("%", "\bmod ")
    
    return back



def transform_vars(var_list: list, data: dict, bibs: dict) -> (list, list, list):
    """
    Evaluates all variables in a formula and returns lists with their respective LaTeX-variables
    or values and units or only values.

    Parameters
    ----------
    var_list : list
        The list of variables in a formula.
    data : dict
        The main dictionary with all inputed variables.
    bibs : dict
        The dictionary containing the additional variables.

    Returns
    -------
    var_list : list
        A list to input into the formula showing all LaTeX-variables.
    tex_val : list
        A list to input into the formula showing all values and units.
    py_val : list
        A list to into into the formula with all values.

    """
    #TODO bei x.000 nur x ausgeben
    #TODO abhängig von größe der Zahl Standardgenauigkeit ändern oder in Exponentialdarstellung wechseln
    tex_val = var_list[:]
    py_val = var_list[:]
    
    for i, var in enumerate(var_list):
        if is_float(var):
            continue
        elif var in tex_commands:
            py_val[i] = "np." + var
            if var != "e":
                tex_val[i] = var_list[i] = "\\" + var
        elif var in trigo_list:
            py_val[i] = "trigo." + var
            tex_val[i] = var_list[i] = "\\" + var[:-1]
        elif var in ("min", "max"):
            tex_val[i] = var_list[i] = "\\" + var
        elif var == "abs":
            tex_val[i] = var_list[i] = ""
        elif var in data:
            py_val[i] = data[var]["res"]
            value_in = exponential_rounding(data[var]["res"], data[var]["prec"])
            #str(round(data[var]["res"], None if data[var]["prec"] == 0 else data[var]["prec"]))      
                # Integer, falls Rundung auf Null
            tex_val[i] = "".join(("\\SI{", value_in, "}{", data[var]["tex_un"], "}"))
            var_list[i] = data[var]["tex_var"]
        else:
            found = False
            
            for bib in bibs.values():
                if var in bib:
                    py_val[i] = bib[var]["res"]
                    value_in = str(round(bib[var]["res"], bib[var]["prec"]))
                    tex_val[i] = "".join(("\\SI{", value_in, "}{", bib[var]["tex_un"], "}"))
                    var_list[i] = bib[var]["tex_var"]
                    found = True
                    break #TODO nur break, wenn anderer Teil erreicht automatisch nicht gefunden
            
            if found == False:
                #nothing found
                #TODO raise exception
                pass
        
    return var_list, tex_val, py_val



def vars_in_short_tex(short_formula: str, var_list: list) -> str:
    """Inputs all variables from var_list into short_tex"""
    #TODO statt Fragezeichen noch selteneres verwenden (Paragraph oder Tilde)
        #in funct_indicator umdefinieren
    
    for var in var_list:
        short_formula = short_formula.replace("?", str(var), 1)
        
    return short_formula



def vars_in_short_form(short_formula: str, var_list: list) -> str:
    """Inputs all variables from var_list into short_formula"""
    #TODO statt Fragezeichen noch selteneres verwenden (Paragraph oder Tilde)
    short_formula = short_formula.replace("~", "?")
    short_formula = short_formula.replace("$", "?")
    short_formula = short_formula.replace("°", "?")
    
    for var in var_list:
        short_formula = short_formula.replace("?", str(var), 1)
        
    return short_formula



#TODO um Werte mit negativem Vorzeichen in Python-Formel und in val-Formel Klammer setzen
def py_eval(formula: str) -> float:
    """Calculates the result of the formula."""
    return eval(formula)
 


def add_brackets(tex_val: str) -> str:
    """
    Adds a pair of brackets around the base of a power if needed.

    Parameters
    ----------
    formula : str
        The processed tex_val-string.

    Returns
    -------
    str
        The tex_val-string with added brackets.

    """
    def search_curly(pos):
        numcorr, numdiff = 0, 0
        while True:
            index = tex_val.rfind("{", 0, pos)
            numdiff += tex_val.count("}", index, pos)
            if numdiff == numcorr:
                return index
            numcorr += 1
            pos = index
        
    index_last = 0
    
    while True:
        index = tex_val.find("^", index_last)
        if index == -1:
            break
        elif tex_val[index-1] == "}":
            index_start = search_curly(index-1)
            if tex_val[index_start-1] == "}":
                index_start = search_curly(index_start-1) - 3
                tex_val = "".join((tex_val[:index_start], "\\left(", tex_val[index_start:index], "\\right)", tex_val[index:]))
                index_last = index + 14
            else:
                index_last = index + 1
        else: 
            index_last = index + 1
            
    return tex_val



def main(formula: str, data: dict, bibs: dict) -> (float, str, str):
    """
    Calculates the result of a formula and its LaTeX-representations given all other variables.

    Parameters
    ----------
    formula : str
        The formula, which should be processed.
    data : dict
        A dictionary containing all other variables and their results.
    bibs : dict
        A dictionary containing additional variables.

    Returns
    -------
    py_res : float
        The result of the formula.
    tex_var : str
        The formula, where the variables are replaced by their LaTeX-representations.
    tex_val : str
        The formula, where the variables are replaced by their values and units.

    """
    short_formula, var_list = find_vars(formula)
    
    short_tex = formula_to_tex(short_formula)
    
    tex_vars, tex_vals, py_vals = transform_vars(var_list, data, bibs)
    
    py_res = py_eval(vars_in_short_form(short_formula, py_vals))
    tex_var, tex_val = vars_in_short_tex(short_tex, tex_vars), vars_in_short_tex(short_tex, tex_vals)
    
    if "}^" in tex_val:
        tex_val = add_brackets(tex_val)
            
    return (py_res, tex_var, tex_val)
    
