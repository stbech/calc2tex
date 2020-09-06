"""
    calc2tex.trigo
    ~~~~~~~~~~~~~~

    Implements trigonometric functions that accept
    degree and gon as arguments.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""


from numpy import pi, sin, cos, tan, arcsin, arccos, arctan

sinD = lambda arg: sin(arg*pi/180)
cosD = lambda arg: cos(arg*pi/180)
tanD = lambda arg: tan(arg*pi/180)

sinG = lambda arg: sin(arg*pi/200)
cosG = lambda arg: cos(arg*pi/200)
tanG = lambda arg: tan(arg*pi/200)

arcsinD = lambda arg: arcsin(arg)*180/pi
arccosD = lambda arg: arccos(arg)*180/pi
arctanD = lambda arg: arctan(arg)*180/pi

arcsinG = lambda arg: arcsin(arg)*200/pi
arccosG = lambda arg: arccos(arg)*200/pi
arctanG = lambda arg: arctan(arg)*200/pi

