"""
    calc2tex.calc2tex
    ~~~~~~~~~~~~~~~~~

    Implements a class which contains a processed dictionary
    of values and formulas.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


from calc2tex import parse_txt
from .settings import language
import json


class Calc2tex:
    def __init__(self, filename: str, lang: str="DE"):
        self.data, self.bibs = parse_txt.main(filename)
        #print(self.bibs)
        self.lang = lang
    
    
    def to_json(self, output: str) -> None:
        """Exports the data-dictionary ta a json-file."""
        if "." not in output:
            output += ".json"
        with open(output, "w") as file:
            file.write(json.dumps(self.data, indent=4))
            
        return ""
    
    
    def _search(self, py_var: str, lookup: str) -> str:
        """Searches for a variable and its sub-key inside the data-dictionary."""
        if py_var in self.data:
            return self.data[py_var][lookup]
        else:
            return "??"
            #TODO zum exceptions-dict hinzufügen
    
    
    def name(self, py_var: str) -> str:
        """Returns the name of a variable"""
        return self._search(py_var, "tex_var")
    
    
    def var(self, py_var: str) -> str:
        """Returns the formula with inputed variables."""
        return self._search(py_var, "var_in")
    
    
    def val(self, py_var: str) -> str:
        """Returns the formula with inputed values."""
        return self._search(py_var, "val_in")
    
    
    def sub_res(self, py_var: str) -> str:
        if self._search(py_var, "type") in  ("minmax", "if"):
            #TODO zusätzlicher Teilschritt in long aufrufen
            return " = " + self._search(py_var, "sub_res")
        else:
            return ""
    
    
    def raw(self, py_var: str, precision: int=None):
        """Returns the result with a certain precision"""
        if precision == None:
            precision = self._search(py_var, "prec")
        return str(round(self._search(py_var, "res"), precision))
    
    
    def res(self, py_var: str, precision: int=None) -> str:
        """Returns the result and its unit with a certain precision"""
        return "".join(("\\SI{", self.raw(py_var, precision), "}{", self.unit(py_var), "}"))
    
    
    def unit(self, py_var: str) -> str:
        """Returns the unit."""
        back = self._search(py_var, "tex_un")
        #TODO soll es überhaupt zurückgegeben werden
        # if back == "":
        #     back = "[-]"
        return back
    
    
    def short(self, py_var: str, precision: int=None) -> str:
        """Displays the name and value of a variable."""
        return " ".join((self.name(py_var), "&=", self.res(py_var, precision)))
    
    
    def long(self, py_var: str, precision: int=None) -> str:
        """Displays complete formula."""
        if self._search(py_var, "var") == "form":
            if self.var(py_var) == self.val(py_var):
                return "".join((self.name(py_var), " &= ", self.val(py_var), self.sub_res(py_var), " = ", self.res(py_var, precision)))
            else:
                return "".join((self.name(py_var), " &= ", self.var(py_var), " = ", self.val(py_var), self.sub_res(py_var), " = ", self.res(py_var, precision)))
        else:
            return self.short(py_var, precision)
    
    
    def mult(self, first: str, last: str, precision: int=None) -> str:
        """Displays multiple formulas at once."""
        back = ""
        found = False
        
        for key, value in self.data.items():
            if key == first:
                found = True
            if found == True:
                back += self.long(key, precision) + "\\\\\n"
            if key == last:
                break
                
        return back[:-3]
    
    
    #TODO zweispaltige Tabelle, dafür val-counter in read_file einbauen
        #oder die \n in gesamten Rückgabestring zählen und beim x-ten \n aufteilen über minipage?
    def table(self, columns: int=1) -> str:
        """
        Extracts the variables with predefined values from the main dictionary and parses them into a long string,
        which evaluates ta a table in LaTeX.

        Returns
        -------
        str
            The complete code block for displaying all input values.

        """
        start = ("\\begin{table}[htbp]", "\t\\centering", "\t\\caption{" + language[self.lang]['table']['header']+"}", 
                 "\t\\label{tab:input_val}", "\t\\begin{tabular}{lcc}", "\t\t\\toprule", 
                 "".join(("\t\t", language[self.lang]['table']['var'], " & ", language[self.lang]['table']['val'], " & ", language[self.lang]['table']['unit'], "\\\\")), 
                 "\t\t\\midrule", "")
        end = ("\t\t\\bottomrule", "\t\\end{tabular}", "\\end{table}")
        
        tab = "\n".join(start)
        for value in self.data.values():
            if value["var"] == "form":
                break
            
            if value["tex_un"] == "":
                unit = "-"
            else:
                unit = value["tex_un"]
                    
            tab += "".join(("\t\t$", value["tex_var"], "$ &", str(round(value["res"], value["prec"])), " & $\\si{", unit, "}$\\\\\n"))
            
        tab += "\n".join(end)
        
        return tab
    
    