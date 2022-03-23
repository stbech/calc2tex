"""
    calc2tex.calc2tex
    ~~~~~~~~~~~~~~~~~

    Implements a class which contains a processed dictionary
    of values and formulas.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""

#TODO Ergebnisse in eine python-Datei schreiben

from calc2tex import parse_txt
from .settings import language
from .helpers import search_bracket, exponential_rounding
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
    
    
    def val(self, py_var: str, nounit=False) -> str:
        """Returns the formula with inputed values."""
        if nounit:
            #search for \SI{ -> suche danach die öffnende Klammer und die dazugehörige schließende lösche alles dazwischen bzw. schreibe Rest in neue Variable
            val = self._search(py_var, "val_in")
            red_val = ''
            index = 0
            
            while '\SI{' in val[index:]:
                start_num = val.index('\SI{', index) + 4
                end_num = search_bracket(val, start_num, 1, True)
                start_unit= end_num+1
                end_unit = search_bracket(val, start_unit, 1, True)
                red_val += val[index:start_unit+1]
                index = end_unit
            
            red_val += val[index:]
            
            
            # print(nounit, start_unit, end_unit)
            # print(val),
            # print('0123456789'*(len(val)//10+1))
            # print(red_val)
            return red_val
        else:
            return self._search(py_var, "val_in")
    
    
    #TODO subres auch mit Option nounit
    def sub_res(self, py_var: str) -> str:
        if self._search(py_var, "type") in ("minmax", "if"):
            #TODO zusätzlicher Teilschritt in long aufrufen
            return self._search(py_var, "sub_res")
        else:
            return ""
    
    
    #TODO ab 1e4 (oder exponential_break - accuracy/precision) Anzahl Nachkommastellen reduzieren
    #TODO Präzision 0 soll keine Nachkommastellen darstellen
    def raw(self, py_var: str, precision: int=None):
        """Returns the result with a certain precision"""
        if precision == None:
            precision = self._search(py_var, "prec")
        
        #print(str(round(self._search(py_var, "res"), None if precision == 0 else precision)) )
        return exponential_rounding(self._search(py_var, "res"), precision)
        #return str(round(self._search(py_var, "res"), None if precision == 0 else precision))   # Integer, falls Rundung auf Null
    
   
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
    
  
    #TODO Option ohne Einheiten darstellen -> nounit=True, an alle Untereinheiten weitergeben suche alle SI-Befehle und leere zweite geschweifte Klammer (auch als globale Option?)
    #TODO split-Argument einführen
    #TODO falls res=val nur eins darstellen
    def long(self, py_var: str, precision: int=None, nounit: bool=False, split: tuple=None) -> str:
        """Displays complete formula."""
        split = tuple([split]) if type(split) == int else split       # convert integer to tuple
        
        if self._search(py_var, "var") == "form":
            calculations = [self.var(py_var), self.val(py_var, nounit), self.sub_res(py_var), self.res(py_var, precision)]
            calculations = [item for item in calculations if item]
            
            if self.var(py_var) == self.val(py_var):
                if not split:
                    #TODO auch auf calculations beziehen
                    return self.name(py_var) + " &= " + " = ".join(calculations[1:])
                    #return "".join((self.name(py_var), " &= ", self.val(py_var, nounit), self.sub_res(py_var), " = ", self.res(py_var, precision)))
                else:
                    string = self.name(py_var) + " &= "
                    elem_old = 1
                    
                    for elem in split:
                        string += " = ".join(calculations[elem_old:elem]) + "\\notag\\\\\n&="
                        elem_old = elem
                        
                    string += " = ".join(calculations[elem_old:])
                    return string
            else:
                if not split:
                    return self.name(py_var) + " &= " + " = ".join(calculations)
                    #return "".join((self.name(py_var), " &= ", self.var(py_var), " = ", self.val(py_var, nounit), self.sub_res(py_var), " = ", self.res(py_var, precision)))
                else:
                    string = self.name(py_var) + " &= "
                    elem_old = 0
                    
                    for elem in split:
                        string += " = ".join(calculations[elem_old:elem]) + "\\notag\\\\\n&="
                        elem_old = elem
                        
                    string += " = ".join(calculations[elem_old:])
                    return string
        else:
            return self.short(py_var, precision)
    
  
    #TODO Warnung wenn Start- oder Endwert nicht gefunden
    def mult(self, first: str, last: str, precision: int=None, nounit: bool=False) -> str:
        """Displays multiple formulas at once."""
        back = ""
        found = False
        
        for key, value in self.data.items():
            if key == first:
                found = True
            if found == True:
                back += self.long(key, precision, nounit) + "\\\\\n"
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
    
    