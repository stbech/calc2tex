# -*- coding: utf-8 -*-
"""
    calc2tex.settings
    ~~~~~~~~~~~~~~~~~

    Stores customizable variables.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


# from importlib import resources
#TODO requires python 3.7
#TODO Konstanten und anpassbare Sachen hier auslagern einheitendatenbank
#TODO in txt auslagern und immer neu einlesen

# def read():
    
#     with resources.open_text("calc2tex", "settings.txt") as file:
#         text = file.readline()
#     
#     return text

language = {"DE": 
                {"table":
                     {"header": 'Eingangsgr"o"sen', "var": "Variable", "val": "Wert", "unit": "Einheit"},
                "if": "falls",
                },
            "EN": 
                {"table": 
                     {"header": "input values", "var": "variable", "val": "value", "unit": "unit"},
                "if": "if",
                }
            }

accuracy = 3

exponential_break = 6    # sets exponent, at which number should be convert to exponential representation 

units = {"singleun": {"m": "\\meter", "g": "\\gram", "A": "\\ampere", "C": "\\coulomb", "K": "\\kelvin", "s": "\\second", "J": "\\joule", "N": "\\newton",
             "V": "\\volt", "W": "\\watt", "h": "\\hour", "l": "\\litre", "t": "\\tonne", "d": "\\day", "a": "\\year", "°": "\\degree"},
         "singlepre": {"f": "\\femto", "p": "\\pico", "n": "\\nano", "m": "\\milli", "c": "\\centi", "d": "\\dezi", "h": "\\hecto", "k": "\\kilo",
             "M": "\\mega", "G": "\\giga", "T": "\\tera", "P": "\\peta"},
         "doubleun": {"ha": "\\hectare", "Pa": "\\pascal", "cd": "\\candela", "Bq": "\\bequerel", "Hz": "\\hertz",
             "lm": "\\lumen", "Sv": "\\sievert", "dB": "\\decibel", "°C": "\\degreeCelsius", "Nm": "\\newton\\meter", "°C": "\\degreeCelsius"},
         "doublepre": {"mu": "\\micro", "da": "\\deca"},
         "tribleun": {"min": "\\minute", "mol": "\\mole", "bar": "\\bar", "ohm": "\\ohm", "rad": "\\radian",
             "gon": "\\gon", "deg": "\\degree"}}


mult_sign = "\\cdot" #others: \times, \star, \ast

quotation_marks = ("\\lq ", "\\text{\\rq}")

check_symb = {"True": "\\qquad\\checkmark", "False": "\\qquad\\lightning"}

keywords = ("acc", "type")

types = ("iter", "if", "eval", "tab")       #noch nicht implementiert
