"""
    calc2tex.calc_formula
    ~~~~~~~~~~~~~~~~~~~~~

    Processes a formula into valid LaTeX and
    calculates its value.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


from .helpers import is_float, search_char, search_bracket, exponential_rounding, intfloat
#from .settings import mult_sign #ersetze mit settings.mult_sign
from calc2tex import settings
import re
#Imports for evaluating formula:
import numpy as np
from calc2tex import trigo
from calc2tex import calc_formula

search_cond = re.compile(r"[!<=>]=?")  #a pattern that recognizes conditional in expression


# Conditionals: <; >; <=; >=; ==; =; !=; 
def evaluate(formula: str, data: dict, bibs: dict) -> dict:
    
    formula = formula.lstrip("eval")    # remove leading eval
    
    cond_pos = search_cond.search(formula)
    cond_count = search_cond.findall(formula)
    
    if len(cond_count) > 1:
        raise Exception("To many conditionals in eval")
        
    if cond_pos == None:
        left_form = formula.strip()
        right_form = "1.0"
        delimiter = "<="
        #raise Exception("No condition in eval")
        #pass # default <=1.0 for right side?
    else: 
        left_form = formula[:cond_pos.start()].strip()
        right_form = formula[cond_pos.end():].strip()
        delimiter = cond_count[0]
        
    print(left_form, delimiter, right_form)
        
    if is_float(left_form):
        left_dict = {"res": intfloat(left_form), "var_in": None, "val_in": None,}
    else:
        left_tuple = calc_formula.main(left_form, data, bibs)
        left_dict = {"res": left_tuple[0], "var_in": left_tuple[1], "val_in": left_tuple[1],}     
    if is_float(right_form):
        right_dict = {"cond_res": intfloat(right_form), "cond_var_in": None, "cond_val_in": None,}
    else:
        right_tuple = calc_formula.main(right_form, data, bibs)
        right_dict = {"cond_res": right_tuple[0], "cond_var_in": right_tuple[1], "cond_val_in": right_tuple[2],}
     
    print(left_dict, right_dict)   
    fulfilled = False
    
    if (delimiter == "<") and (left_dict["res"] < right_dict["cond_res"]):
        fulfilled = True
    elif (delimiter == "<=") and (left_dict["res"] <= right_dict["cond_res"]):
        fulfilled = True
    elif (delimiter == ">") and (left_dict["res"] > right_dict["cond_res"]):
        fulfilled = True 
    elif (delimiter == ">=") and (left_dict["res"] >= right_dict["cond_res"]):
        fulfilled = True 
    elif (delimiter == "!=") and (left_dict["res"] != right_dict["cond_res"]):
        fulfilled = True 
    elif (delimiter == "=" or delimiter == "==") and (left_dict["res"] == right_dict["cond_res"]):
        fulfilled = True 
    print(fulfilled)
    
    #if len()
    
    # eval raus an <=> splitten, beide Teile separat von calc_formula verarbeiten lassen
    #TODO on change to python 3.9 -> dict merge with |
    return {"cond": delimiter,**left_dict, **right_dict, "bool": fulfilled}#{"res": None, "var_in": None, "val_in": None, "cond_res": None, "cond_var_in": None, "cond_val_in": None,}
   
    
   