"""
    calc2tex
    ~~~~~~~~

    calc2tex is a Python package to evaluate formulas
    and export a pretty version to LaTeX. It takes in
    a list of variables and formulas written using Python's
    syntax and creates valid LaTeX-code for values and 
    formulas that can be inserted in a tex-file.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


from .calc2tex import Calc2tex
from .parse_tex import process_tex

