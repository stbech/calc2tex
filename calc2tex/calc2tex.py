"""
    calc2tex.calc2tex
    ~~~~~~~~~~~~~~~~~

    Implements a class which contains a processed dictionary
    of values and formulas.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""

# TODO Ergebnisse in eine python-Datei schreiben

from calc2tex import parse_txt
from .settings import language, check_symb
from .helpers import search_bracket, exponential_rounding
import json


class Calc2tex:
    def __init__(self, filename: str, lang: str="DE"):
        self.data, self.bibs = parse_txt.main(filename)
        # print(self.bibs)
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
            # TODO zum exceptions-dict hinzufügen


    def name(self, py_var: str) -> str:
        """Returns the name of a variable"""
        return self._search(py_var, "tex_var")


    def var(self, py_var: str, key: str = "var_in") -> str:
        """Returns the formula with inputed variables."""
        #search = "cond_var_in" if cond else "var_in"
        return self._search(py_var, key)


    def val(self, py_var: str, nounit: bool=False, key: str="val_in") -> str:
        """Returns the formula with inputed values."""
        #key = key if key else "val_in"
        val = self._search(py_var, key)

        if (val == None) or not(nounit):
            return val

        if nounit:
            # search for \SI{ -> suche danach die öffnende Klammer und die dazugehörige schließende lösche alles dazwischen bzw. schreibe Rest in neue Variable
            red_val = ''
            index = 0

            while '\SI{' in val[index:]:
                start_num = val.index('\SI{', index) + 4
                end_num = search_bracket(val, start_num, 1, True)
                start_unit = end_num+1
                end_unit = search_bracket(val, start_unit, 1, True)
                red_val += val[index:start_unit+1]
                index = end_unit
            # try:
            #     while '\SI{' in val[index:]:
            #         start_num = val.index('\SI{', index) + 4
            #         end_num = search_bracket(val, start_num, 1, True)
            #         start_unit= end_num+1
            #         end_unit = search_bracket(val, start_unit, 1, True)
            #         red_val += val[index:start_unit+1]
            #         index = end_unit
            # except:
            #     print(py_var, search, val)

            red_val += val[index:]

            return red_val
        else:
            return self._search(py_var, key)


    # TODO subres auch mit Option nounit
    def sub_res(self, py_var: str) -> str:
        if self._search(py_var, "type") in ("minmax", "if"):
            # TODO zusätzlicher Teilschritt in long aufrufen
            return self._search(py_var, "sub_res")
        else:
            return ""


    # TODO ab 1e4 (oder exponential_break - accuracy/precision) Anzahl Nachkommastellen reduzieren
    # TODO Präzision 0 soll keine Nachkommastellen darstellen
    def raw(self, py_var: str, precision: int=None, key: str="res"):
        """Returns the result with a certain precision"""
        #search = "cond_res" if cond else "res"

        # if py_var == 'delta_s':
        #     print(precision)

        if precision == None:
            precision = self._search(py_var, "prec")

        # if py_var == 'delta_s':
        #     print(exponential_rounding(self._search(py_var, search), precision))
        #     print(precision)
        #print(str(round(self._search(py_var, "res"), None if precision == 0 else precision)) )
        res = self._search(py_var, key)
        if res != "??" and type(res) != str:
            return exponential_rounding(res, precision)
        if res != "??" and type(res) == str:
            return res
        else:
            return '??'
        # return str(round(self._search(py_var, "res"), None if precision == 0 else precision))   # Integer, falls Rundung auf Null


    def unit(self, py_var: str) -> str:
        """Returns the unit."""
        back = self._search(py_var, "tex_un")
        # TODO soll es überhaupt zurückgegeben werden
        # if back == "":
        #     back = "[-]"
        return back


    def res(self, py_var: str, precision: int=None, key: str="res") -> str:
        """Returns the result and its unit with a certain precision"""
        #search = "cond_res" if cond else "res"

        if self._search(py_var, key) == "??":
            return "??"

        if self._search(py_var, "var") == "str" or self._search(py_var, "var") == "str_form":
            # TODO anpassen, ob Einheit gewollt
            # TODO Option Anführungszeichen zu zeigen? -> abhängig davon, ob in Matheumgebung (ja) oder nicht (nein)
            return "".join(("\\text{", self._search(py_var, key), "}\\si{", self.unit(py_var), "}"))
        else:
            if self.unit(py_var) == "":
                return "".join(("\\num{", self.raw(py_var, precision, key), "}"))
            else:
                return "".join(("\\SI{", self.raw(py_var, precision, key), "}{", self.unit(py_var), "}"))


    def cond(self, py_var: str) -> str:
        return self._search(py_var, "cond")


    def check(self, py_var: str) -> str:
        return check_symb[str(self._search(py_var, "bool"))]


    def short(self, py_var: str, precision: int=None, check: bool=False) -> str:
        """Displays the name and value of a variable."""
        if self._search(py_var, "var") == "eval":
            if self.name(py_var) == "":
                string = "".join(("&\\hspace{5.1mm} ", self.res(py_var, precision), self.cond(py_var), self.res(py_var, precision, "cond_res")))
            else:
                string = " ".join((self.name(py_var), "&=", self.res(py_var, precision), self.cond(py_var), self.res(py_var, precision, "cond_res")))

            add = self.check(py_var) if check else ""
            return string + add
        else:
            if self.name(py_var) == "":
                return "&\\hspace{5.1mm} " + self.res(py_var, precision)
            else:
                return " ".join((self.name(py_var), "&=", self.res(py_var, precision)))
        # return " ".join((self.name(py_var), "&=", self.res(py_var, precision)))


    def _long_shortif(self, py_var: str, precision: int=None, nounit: bool=False, noval: bool=False, split: tuple=None) -> str:
        calculations = [self.var(py_var, "short_var_in"), self.val(py_var, nounit, "short_val_in"), self.sub_res(py_var), self.res(py_var, precision)]
        calculations = [item for item in calculations if item]
        
        if noval:
            calculations.remove(self.val(py_var, nounit, "short_val_in"))
        else:
            if self.var(py_var, "short_var_in") == self.val(py_var, False, "short_val_in"):
                calculations.remove(self.var(py_var, "short_var_in"))
            if self.res(py_var, precision) == self.val(py_var, False, "short_val_in"):
                calculations.remove(self.val(py_var, nounit, "short_val_in"))

        if self.name(py_var) == "":
            string = "&\\hspace{5.1mm} "
        else:
            string = self.name(py_var) + " &= "

        if not split:
            return string + " = ".join(calculations)
        else:
            elem_old = 0

            for elem in split:
                if elem >= len(calculations):
                    continue
                string += " = ".join(calculations[elem_old:elem]) + "\\notag\\\\\n&="
                elem_old = elem

            string += " = ".join(calculations[elem_old:])
            return string
    
        
    def _long_form(self, py_var: str, precision: int=None, nounit: bool=False, noval: bool=False, split: tuple=None) -> str:
        calculations = [self.var(py_var), self.val(py_var, nounit), self.sub_res(py_var), self.res(py_var, precision)]
        calculations = [item for item in calculations if item]
            
        if noval:
            calculations.remove(self.val(py_var, nounit))
        else:
            if self.var(py_var) == self.val(py_var):
                calculations.remove(self.var(py_var))
            if self.res(py_var, precision) == self.val(py_var):
                calculations.remove(self.val(py_var, nounit))

        if self.name(py_var) == "":
            string = "&\\hspace{5.1mm} "
        else:
            string = self.name(py_var) + " &= "

        if not split:
            return string + " = ".join(calculations)
        else:
            elem_old = 0

            for elem in split:
                if elem >= len(calculations):
                    continue
                string += " = ".join(calculations[elem_old:elem]) + "\\notag\\\\\n&="
                elem_old = elem

            string += " = ".join(calculations[elem_old:])
            return string
        
    
    def _long_eval(self, py_var: str, precision: int=None, nounit: bool=False, noval: bool=False, split: tuple=None, check: bool=False) -> str:
        left_calc = [self.var(py_var), self.val(py_var, nounit), self.res(py_var, precision)]   # subres removed
        right_calc = [self.var(py_var, "cond_var_in"), self.val(py_var, nounit, "cond_val_in"), self.res(py_var, precision, "cond_res")]

        if noval:
            left_calc.remove(self.val(py_var, nounit))
            right_calc.remove(self.val(py_var, nounit, "cond_val_in"))
        else:
            if self.var(py_var) == self.val(py_var):
                left_calc.remove(self.var(py_var))
            if self.res(py_var) == self.val(py_var):
                left_calc.remove(self.val(py_var, nounit))

            if self.var(py_var, "cond_var_in") == self.val(py_var, False, "cond_val_in"):
                right_calc.remove(self.var(py_var, "cond_var_in"))
            if self.res(py_var, precision, "cond_res") == self.val(py_var, False, "cond_val_in"):
                right_calc.remove(self.val(py_var, nounit, "cond_val_in"))

        left_calc = [item for item in left_calc if item]
        right_calc = [item for item in right_calc if item]
        left_calc.extend(right_calc)
        # print(calculations)

        add = self.check(py_var) if check else ""

        if self.name(py_var) == "":
            string = "&\\hspace{5.1mm} "
        else:
            string = self.name(py_var) + " &= "
        # TODO eval kann nicht beim 0. Gleichheitszeichen abbrechen

        if not split:
            for item in left_calc[:-1]:
                if item != self.res(py_var, precision):
                    string += item + " = "
                else:
                    string += "".join((item, " ", self.cond(py_var), " "))

            return string + left_calc[-1] + add  # + " = ".join(left_calc)
        else:
            #elem_old = 1
            split_iter = iter(split)
            splitter = next(split_iter)

            for i, item in enumerate(left_calc[:-1]):
                # print(string)
                #print(i, splitter, left_calc[i])
                if i+1 == splitter:
                    if splitter == split[-1]:
                        splitter = -1
                    else:
                        splitter = next(split_iter)

                    if item != self.res(py_var, precision):
                        string += item + "\\notag\\\\\n&= "
                    else:
                        string += "".join((item, "\\notag\\\\\n& ",
                                          self.cond(py_var), " "))
                else:
                    if item != self.res(py_var, precision):
                        string += item + " = "
                    else:
                        string += "".join((item, " ",
                                          self.cond(py_var), " "))

            # for elem in split:
            #    string += " = ".join(left_calc[elem_old:elem]) + "\\notag\\\\\n&="
            #    elem_old = elem

            #string += " = ".join(left_calc[elem_old:])
            return string + left_calc[-1] + add


    # TODO Option ohne Einheiten darstellen -> nounit=True, an alle Untereinheiten weitergeben suche alle SI-Befehle und leere zweite geschweifte Klammer (auch als globale Option?)
    # TODO split-Argument einführen
    # TODO falls bei if/shortif val_in nur eine Zahl -> Darstellung von Var und res -> ändern
    def long(self, py_var: str, precision: int=None, nounit: bool=False, noval: bool=False, split: tuple=None, check: bool=False, shortif: bool=False) -> str:
        """Displays complete formula."""
        split = tuple([split]) if type(split) == int else split       # convert integer to tuple
        
        form_type = self._search(py_var, "var")

        if form_type == "if" and shortif:
            return self._long_shortif(py_var, precision, nounit, noval, split)
        # elif form_type == "if":
        #     return self._long_shortif(py_var, precision, nounit, noval, split)
        elif form_type == "form" or form_type == "if":
            return self._long_form(py_var, precision, nounit, noval, split)
        elif form_type == "eval":
            return self._long_eval(py_var, precision, nounit, noval, split, check)
        else:
            return self.short(py_var, precision)


    # TODO Warnung wenn Start- oder Endwert nicht gefunden
    def mult(self, first: str, last: str, precision: int = None, short: bool = False, nounit: bool = False, noval: bool = False, check: bool = False) -> str:
        """Displays multiple formulas at once."""
        back = ""
        found = False

        for key, value in self.data.items():
            if key == first:
                found = True
            if found:
                if short:
                    back += self.short(key, precision, check) + "\\\\\n"
                else:
                    back += self.long(key, precision, nounit, noval, None, check) + "\\\\\n"
            if key == last:
                break
            
        if found == False:
            back = "\\text{mult}??   "  # start variable not found

        return back[:-3]

    # TODO table funktioniert nicht ohne first, last anzugeben -> fix value table

    def table(self, first: str = None, last: str = None, columns: int = 1) -> str:
        """
        Extracts the variables with predefined values from the main dictionary and parses them into a long string,
        which evaluates ta a table in LaTeX.

        Returns
        -------
        str
            The complete code block for displaying all input values.

        """

        if first == None:
            if columns >= 2:
                header = " & ".join(["".join((language[self.lang]['table']['var'], " & ", language[self.lang]['table']['val'], " & ", language[self.lang]['table']['unit']))]*columns)
                start = ("\\begin{table}[htbp]", "\t\\centering", "\t\\caption{" + language[self.lang]['table']['header']+"}",
                         "\t\\label{tab:input_val}", "".join(("\t\\begin{tabular}{", "@{\\hspace{15mm}}".join(columns*["lcc"]), "}")), "\t\t\\toprule",
                         "".join(("\t\t", header, "\\\\")), "\t\t\\midrule", "")
            else:
                start = ("\\begin{table}[htbp]", "\t\\centering", "\t\\caption{" + language[self.lang]['table']['header']+"}",
                         "\t\\label{tab:input_val}", "\t\\begin{tabular}{lcc}", "\t\t\\toprule",
                         "".join(("\t\t", language[self.lang]['table']['var'], " & ", language[self.lang]['table']['val'], " & ", language[self.lang]['table']['unit'], "\\\\")),
                         "\t\t\\midrule", "")
                
            end = ("\t\t\\bottomrule", "\t\\end{tabular}", "\\end{table}")
        else:
            if columns >= 2:
                header = " & ".join(["".join((language[self.lang]['table']['var'], " & ", language[self.lang]['table']['val'], " & ", language[self.lang]['table']['unit']))]*columns)
                start = ("".join(("\t\\begin{tabular}{", "@{\\hspace{15mm}}".join(columns*["lcc"]), "}")), "\t\t\\toprule",
                         "".join(("\t\t", header, "\\\\")), "\t\t\\midrule", "")
            else:
                start = ("\t\\begin{tabular}{lcc}", "\t\t\\toprule",
                     "".join(("\t\t", language[self.lang]['table']['var'], " & ", language[self.lang]['table']['val'], " & ", language[self.lang]['table']['unit'], "\\\\")),
                     "\t\t\\midrule", "")
                
            end = ("\t\t\\bottomrule", "\t\\end{tabular}")


        tab = ""

        if first == None:
            for key, value in self.data.items():
                if value["var"] == "form" or key == last:
                    break

                if value["tex_un"] == "":
                    unit = "-"
                else:
                    unit = value["tex_un"]

                tab += "".join(("\t\t$", value["tex_var"], "$ &", str(round(value["res"], value["prec"])), " & $\\si{", unit, "}$\\\\\n"))

        else:
            found = False

            for key, value in self.data.items():

                if value["tex_un"] == "":
                    unit = "-"
                else:
                    unit = value["tex_un"]

                if key == first:
                    found = True
                if found == True:
                    tab += "".join(("\t\t$", value["tex_var"], "$ & \\num{", str(round(value["res"], value["prec"])), "} & $\\si{", unit, "}$\\\\\n"))
                if key == last:
                    break
         
                
        if columns >= 2:
            length = tab.count("\n")
            
            new_line, old_line = 0, 0
            
            column_list = []
            for _ in range(columns):
                for _ in range(length//columns if length % columns == 0 else length//columns + 1):
                    new_line = tab.find("\n", new_line+1)
                    
                column_list.append(tab[old_line: new_line].split("\n"))
                old_line = new_line + 1
            
            max_length = len(column_list[0])
            
            tab = ""
            for i in range(len(column_list[0])):
                line = "\t\t"
                for k in range(columns):
                    if i < len(column_list[k]) :
                        line += column_list[k][i].lstrip("\t").rstrip("\\\\\n") + " & "
                
                tab += line[:-3] + "\\\\\n"
            
        
        tab = "\n".join(start) + tab + "\n".join(end)

        return tab
