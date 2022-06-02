"""
    calc2tex.calc_formula
    ~~~~~~~~~~~~~~~~~~~~~

    Processes a formula into valid LaTeX and
    calculates its value.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


from .helpers import is_float, intfloat
from .settings import quotation_marks
import re
from calc2tex import calc_formula

search_cond = re.compile(r"[!<=>]=?")  #a pattern that recognizes conditional in expression



def delimiters(delimiter: str, left_val: float, right_val: float) -> (str, bool):

    if (delimiter == "<"):
        tex_delimiter = "<"
        fulfilled = True if (left_val < right_val) else False
    elif (delimiter == "<="):
        tex_delimiter = "\\leq"
        fulfilled = True if (left_val <= right_val) else False
    elif (delimiter == ">"):
        tex_delimiter = ">"
        fulfilled = True if (left_val > right_val) else False
    elif (delimiter == ">="):
        tex_delimiter = "\\geq"
        fulfilled = True if (left_val >= right_val) else False
    elif (delimiter == "!="):
        tex_delimiter = "\\neq"
        fulfilled = True if (left_val != right_val) else False
    elif (delimiter == "=" or delimiter == "=="):
        tex_delimiter = "="
        fulfilled = True if (left_val == right_val) else False
        
    return tex_delimiter, fulfilled



def string_comb(formula: str, data: dict, bibs: dict) -> dict:
    
    formula = formula.lstrip("string")      # remove leading if 
    
    parts = formula.split("+")           # split at every elif
    #parts = [part.strip() for part in parts]
    
    res = ""
    
    #print(parts)
    for part in parts:
        part = part.strip()
        if (part.startswith("'") and part.endswith("'")) or (part.startswith('"') and part.endswith('"')):
            res += part.strip("\"'")#print(part)
        else:
            #TODO vereinfacht keine Multiplikationen/Divisionen zulassen und nur auf data[part][res] zugreifen
            part_tuple = calc_formula.main(part, data, bibs)
            res += str(part_tuple[0])
            #print(part_tuple)
            
    #print(res)
    return {"res": res}
    


#TOOD verschachtelte IFs!
#TODO Werte eingesetzt -> schon auf richtiges reduziert oder alle dargestellt
def ifthenelse(formula: str, data: dict, bibs: dict) -> dict:
    
    formula = formula.lstrip("if")          # remove leading if 
    
    parts = formula.split("elif")           # split at every elif
    parts.extend(parts[-1].split("else"))   # get last element and split at else
    parts.pop(-3)                           # remove element containing else
    
    parts = [elem.strip(" :") for elem in parts]
    form_dicts = []
    result = None
    
    for elem in parts[:-1]:             # iterate over every if/elif condition
        cond, form = elem.split(":")
        cond_pos = search_cond.search(cond)
        
        left = cond[:cond_pos.start()].strip()
        right = cond[cond_pos.end():].strip()
        delimiter = cond[cond_pos.start():cond_pos.end()]
   
        txt_dict = {"left": left, "cond": delimiter, "right": right, "form": form.strip()}
        
        if is_float(left):
            left_dict = {"left_res": intfloat(left), "left_var_in": "\\num{" + left + "}", "left_val_in": None,}
        elif left.startswith('"') or left.startswith("'"):
            left_dict = {"left_res": left.strip("\"'"), "left_var_in": quotation_marks[0] + left.strip("\"'") + quotation_marks[1], "left_val_in": None,}
        else:
            left_tuple = calc_formula.main(left, data, bibs)
            left_dict = {"left_res": left_tuple[0], "left_var_in": left_tuple[1], "left_val_in": left_tuple[2],}     
        
        if is_float(right):
            right_dict = {"right_res": intfloat(right), "right_var_in": "\\num{" + right + "}", "right_val_in": None,}
        elif right.startswith('"') or right.startswith("'"):
            right_dict = {"right_res": right.strip("\"'"), "right_var_in": quotation_marks[0] + right.strip("\"'") + quotation_marks[1], "right_val_in": None,}
        else:
            right_tuple = calc_formula.main(right, data, bibs)
            right_dict = {"right_res": right_tuple[0], "right_var_in": right_tuple[1], "right_val_in": right_tuple[2],}
         
        form_tuple = calc_formula.main(form, data, bibs)
        form_dict = {"res": form_tuple[0], "var_in": form_tuple[1], "val_in": form_tuple[2],} 
        
        tex_delimiter, fulfilled = delimiters(delimiter, left_dict["left_res"], right_dict["right_res"])

        form_dicts.append({**txt_dict, **left_dict, "tex_cond": tex_delimiter, **right_dict, **form_dict})
        
        if fulfilled and result == None:
            result = form_dict["res"]
            shorts = form_dict
    
    
    else_tuple = calc_formula.main(parts[-1], data, bibs)
    else_dict = {"res": else_tuple[0], "var_in": else_tuple[1], "val_in": else_tuple[2],} 
    
    if result == None:
        result = else_dict["res"]
        shorts = else_dict
     
    # combine to one var_in
    var_text = "\\begin{cases}\n"
    iftext = ("falls", "")
    
    for form_dict in form_dicts:
        var_text += "".join(("\t", form_dict["var_in"], " & \\text{", iftext[0], " $", form_dict["left_var_in"], " ", form_dict["tex_cond"], " ", form_dict["right_var_in"], "$}\\\\\n"))
     
    var_text += "".join(("\t", else_dict["var_in"], " & \\text{", iftext[1], "}\\\\\n"))
    var_text += "\\end{cases}\\quad"
        
    return {"var_in": var_text, "val_in": shorts["val_in"], "res": result, "short_var_in": shorts["var_in"], "short_val_in": shorts["val_in"],}


# Conditionals: <; >; <=; >=; ==; =; !=; 
def evaluate(formula: str, data: dict, bibs: dict) -> dict:
    
    formula = formula.lstrip("eval")    # remove leading eval
    
    cond_pos = search_cond.search(formula)
    cond_count = search_cond.findall(formula)
    
    if len(cond_count) > 1:     # More than one conditional expression recognized
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
        
    if is_float(left_form):
        left_dict = {"res": intfloat(left_form), "var_in": None, "val_in": None,}
    else:
        left_tuple = calc_formula.main(left_form, data, bibs)
        left_dict = {"res": left_tuple[0], "var_in": left_tuple[1], "val_in": left_tuple[2],}     
    if is_float(right_form):
        right_dict = {"cond_res": intfloat(right_form), "cond_var_in": None, "cond_val_in": None,}
    else:
        right_tuple = calc_formula.main(right_form, data, bibs)
        right_dict = {"cond_res": right_tuple[0], "cond_var_in": right_tuple[1], "cond_val_in": right_tuple[2],}
      
    #fulfilled = False
    
    tex_delimiter, fulfilled = delimiters(delimiter, left_dict["res"], right_dict["cond_res"])
    # if (delimiter == "<"):
    #     tex_delimiter = "<"
    #     fulfilled = True if (left_dict["res"] < right_dict["cond_res"]) else False
    # elif (delimiter == "<="):
    #     tex_delimiter = "\\leq"
    #     fulfilled = True if (left_dict["res"] <= right_dict["cond_res"]) else False
    # elif (delimiter == ">"):
    #     tex_delimiter = ">"
    #     fulfilled = True if (left_dict["res"] > right_dict["cond_res"]) else False
    # elif (delimiter == ">="):
    #     tex_delimiter = "\\geq"
    #     fulfilled = True if (left_dict["res"] >= right_dict["cond_res"]) else False
    # elif (delimiter == "!="):
    #     tex_delimiter = "\\neq"
    #     fulfilled = True if (left_dict["res"] != right_dict["cond_res"]) else False
    # elif (delimiter == "=" or delimiter == "=="):
    #     tex_delimiter = "=="
    #     fulfilled = True if (left_dict["res"] == right_dict["cond_res"]) else False
    
    #TODO on change to python 3.9 -> dict merge with |
    return {"cond": tex_delimiter, **left_dict, **right_dict, "bool": fulfilled}#{"res": None, "var_in": None, "val_in": None, "cond_res": None, "cond_var_in": None, "cond_val_in": None,}
   
    
   