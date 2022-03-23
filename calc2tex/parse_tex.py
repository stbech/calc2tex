# -*- coding: utf-8 -*-
"""
    calc2tex.parse_tex
    ~~~~~~~~~~~~~~~~~~

    Processes a tex-file and replaces the Python functions
    with their desired LaTeX-expressions.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""
#TODO falls filecontents-Umgebung mit dem Namen der txt-Datei in tex-Datei: entfernen, falls möglich
#TODO eine input.tex in mehrere output.tex aufzuteilen

from .helpers import search_bracket, search_char
from .calc2tex import Calc2tex


def process_tex(in_file: str, out_file: str, show_log: bool=True) ->None:
    commands = []

    with open(in_file) as stdin, open(out_file, "w") as stdout:
        for line in stdin:
            while True:
                if "Calc2tex(" in line:
                    index = line.index("Calc2tex(")
                    bracket = search_bracket(line, index+8, 1)
                    end = line.rindex("=", 0, index)
                    while line[end] == " ":
                        end -= 1
                
                    start = line.rfind(" ", 0, end-1) + 1
                    if start == 0:
                        #TODO durch rfind ersetzen -> wenn kein \t gefunden -> start = 0 oder Regex \s suchen
                        start = line.rindex("\t", 0, end-1) + 1
                
                    commands.append(line[start:end-1] + ".")
                    exec(line[start:bracket+1])
                    line = line.replace(line[start:bracket+1], "")
                else:
                    break
               
            for command in commands:
                while True:
                    if command in line:
                        index = line.index(command)
                        if "%" in line[0:index]:
                            break
                        
                        opening = search_char(line, index, ("("))
                        closing = search_bracket(line, opening, 1)
                        insert = eval(line[index:closing+1])
                        if "\t" == line[index-1]:
                            num = line.count("\t", 0, index)
                            insert = insert.replace("\n", "\n" + "\t"*num)
                        
                        if "$" in line[:index]:
                            insert = insert.replace("&=", "=")
                        
                        line = line.replace(line[index:closing+1], insert)
                    else:
                        break
            
            stdout.write(line)
            
            