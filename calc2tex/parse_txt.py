"""
    calc2tex.parse_to_txt
    ~~~~~~~~~~~~~~~~~~~~~

    Reads in a txt-file, creates a partially filled dictionary and
    calls *calc_unit* and *calc_formula* to fill the dictionary.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""

#TODO Exponential-Darstellung für Zahlen anbieten als zusätzliches Argument
#TODO prüfe auf Verwendung reserviertee Begriffe, z.B. e, pi

from calc2tex import calc_formula
from .settings import accuracy, keywords, types
from .calc_unit import unit_to_tex
from .helpers import is_float
import json, os
from importlib import resources


def read_file(filename: str) -> (dict, dict):
    """
    Parses a txt-file into a dictionary.

    Parameters
    ----------
    filename : str
        The path to a txt-file, containing a semicolon-separated list.

    Returns
    -------
    data : dict
        A dictionary containing the parsed file.
    bibs : dict
        A dictionary containing additional variables.

    """                     
    data = {}                                       #creates an empty container for the information in the file
    bibs = {}
    input_list = []                                 #a list for holding the pre-processed lines 
    
    with open(filename) as file:
        for i, line in enumerate(file, 1):                               #iterates over the lines in file
            save = [str(i)]
            index = line.find("#")
            if index == -1:
                save.extend(line.split(";") )               #splits line on every semi-colon
            else: 
                save.extend(line[:index].split(";"))
            save = [part.strip() for part in save]      #removes leading and trailing whitespace on every substring
            if save[1] == "":                           #empty lines and lines starting with the hash character are ignored
                continue
            elif save[1][0] != "#":
                input_list.append(save)
    
    
    def input_dict(line: str, var: str, tex_var: str, *args: str) -> dict:
        """Returns a partially filled dict for one variable."""
        if var == "val":
            return {"line": line, "var": var, "tex_var": tex_var, "res": args[0],
                    "unit": args[1], "tex_un": None, "prec": args[2]}
        else:
            return {"line": line, "var": var, "tex_var": tex_var, "res": None, 
                    "unit": args[1], "tex_un": None, "type": args[3], "form": args[0], "prec": args[2]}
        
    convert = lambda num: float(num) if '.' in num else int(num) 
    # convert decimal numbers to float and the rest to integers  
    
    
    for line in input_list:                                 #extracts information from pre-processed file into data-container
        if len(line) == 2:                                  #differentiats different cases by length of list
            command, bib_str = line[1].split(":")
            if command.strip() == "use":
                for bib in bib_str.split(","):
                    if "." not in bib:
                        bib = bib.strip() + ".json"
                    bibs[bib.strip()] = None
            
            #TODO zweites dict mit Werten von Bibs, auf Reihenfolge von Einfügen achten falls Doppelkey,
                #erst im aktuellen Verzeichnis schauen-> Aufbau und Verarbeitung wie read-file, dann im Modulverzeichnis Biblio suchen
                #dort als json oder txt speichern, letzteres geringerer Platzbedarf, langsameres parsen; abhängig von Dateiendung verarbeiten
            
        elif is_float(line[3]):
            if keywords[0] in line[-1]:
                data[line[1]] = input_dict(int(line[0]), "val", line[2], convert(line[3]), line[4], int(line[-1][line[-1].index("=")+1:]))
            elif is_float(line[-1]):
                data[line[1]] = input_dict(int(line[0]), "val", line[2], convert(line[3]), line[4], int(line[-1]))
            else:
                data[line[1]] = input_dict(int(line[0]), "val", line[2], convert(line[3]), line[4], accuracy)
                
        elif is_float(line[2]):                         #no tex_var specified, so tex_var is set to py_var
            if keywords[0] in line[-1]:
                data[line[1]] = input_dict(int(line[0]), "val", line[2], convert(line[2]), line[3], int(line[-1][line[-1].index("=")+1:]))
            elif is_float(line[-1]):
                data[line[1]] = input_dict(int(line[0]), "val", line[1], convert(line[2]), line[3], int(line[-1]))
            else:
                data[line[1]] = input_dict(int(line[0]), "val", line[1], convert(line[2]), line[3], accuracy)
                
        elif len(line) >= 4:
            precision, form_type = accuracy, ""
            keys = 0
            for j in range(1,3):
                if keywords[0] in line[-j]:
                    keys += 1
                    precision = int(line[-j][line[-j].index("=")+1:])
                elif keywords[1] in line[-j]:
                    keys += 1
                    form_type = line[-j][line[-j].index("=")+1:].strip()
                elif is_float(line[-j]):
                    keys += 1
                    precision = int(line[-j])
                elif line[-j] in types:
                    keys += 1
                    form_type = line[-j]
                
                            
            if len(line) - keys == 5:
                data[line[1]] = input_dict(int(line[0]), "form", line[2], line[3], line[4], precision, form_type)
            else:
                data[line[1]] = input_dict(int(line[0]), "form", line[1], line[2], line[3], precision, form_type)
                
        else:
            pass 
        
    return data, bibs



def calculate(data: dict, bibs: dict) -> dict:
    """
    Takes the dictionary with the inputs from the txt-file, and returns
    a dictionary with all values and LaTeX-strings calculated.

    Parameters
    ----------
    data : dict
        The unprocessed dictionary.
    bibs : dict
        The processed dictionary containing additional variables.

    Returns
    -------
    dict
        A dictionary, with every value calculated.

    """
    for key in data.keys():
        data[key]["tex_un"] = unit_to_tex(data[key]["unit"])
        if data[key]["var"] == "form":
            data[key]["res"], data[key]["var_in"], data[key]["val_in"] = calc_formula.main(data[key]["form"], data, bibs)
        
    return data



def load_bibs(bibs: dict) -> dict:
    """
    Loads in all bibliographies.

    Parameters
    ----------
    bibs : dict
        A dictionary with the bibs from the txt-file.

    Returns
    -------
    dict
        The dictionary filled with values.

    """
    for bib in bibs.keys():
        if bib in os.listdir():
            if bib[-5:] == ".json":
                pass
            elif bib[-4:] == ".txt":
                bibs[bib], _ = main(bib)
        else:
            #TODO in Standardbibliothek suchen
            pass
        
            
    return bibs



def main(filename: str) -> (dict, dict):
    """
    Reads and calculates a fully filled dictionary to use in the class.

    Parameters
    ----------
    filename : str
        The filename of a txt-file containing the inputs.

    Returns
    -------
    data : dict
        A dictionary with springs for displaying in LaTeX and values.
    bibs : dict
        A dictionary containing external bibliographies.

    """
    data, bibs = read_file(filename)
    bibs = load_bibs(bibs)
    return calculate(data, bibs), bibs
