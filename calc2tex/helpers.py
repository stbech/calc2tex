"""
    calc2tex.helpers
    ~~~~~~~~~~~~~~~~

    Some basic functions that are used in other modules.
    
    :copyright: 2020 by Stefan Becherer
    :license: MIT
"""

from .settings import exponential_break, accuracy


def is_float(number: str) -> bool:
    """Checks if the input-string can be converted ta a valid number."""
    try:
        float(number)
    except:
        return False
    else:
        return True
    
    
#exponential_break = 6   #TODO aus settings
#accuracy = 3
#TODO add trailing whitespaces, to show precision like round(1.0001, 3) -> 1.0, but should be 1.000
#TODO falls a=0 und eingesetzt in cos(a) ->var-Form: cos(0.0) -> wieso?
def exponential_rounding(number: float, precision: int) -> str:
    """Converts number to exponential representation, if above certain threshold"""
    if abs(number) >= 10**exponential_break:
        exponent = len(str(int(number))) - 1
        num = round(number/(10**(exponent - precision))) / 10**precision
        num = int(num) if precision == 0 else num
        
        return str(num) + 'e' + str(exponent)
    
    elif abs(number) >= 10**(exponential_break - precision) and precision == accuracy:
        new_precision = exponential_break - len(str(int(number))) + 1
        
        return str(round(number, None if precision == 0 else new_precision))
      
    #TODO wird durch gewählte Präzision ausgehebelt -> falls precison=10: 10 Nachkommastellen
        # precision durch Standard-accuracy ersetzen
    elif abs(number) < 10**(-accuracy):
        exponent = -(len(str(number)) - len(str(number)[2:].lstrip('0')) - 1)
        num = round(number/(10**(exponent - precision))) / 10**precision
        num = int(num) if precision == 0 else num
        
        return str(num) + 'e' + str(exponent)
    
    else:
        return str(round(number, None if precision == 0 else precision))
    


    
def search_char(string: str, pos: int, chars: tuple) -> int:
    """
    Searches for the index of the next char out of the chars-list.

    Parameters
    ----------
    string : str
        A formula.
    pos : int
        The index, at which searching should be started.
    chars : list
        A list containing strings.

    Returns
    -------
    int
        The index of the next char or if there is no char found the lenght of the string.

    """
    indices = []
    for char in chars:
        #TODO nicht auf try-except statement verlassen -> char in string, dann string.index
        try:
            indices.append(string.index(char, pos))
        except:
            pass
    
    if indices == []:
        return len(string)
    else:
        return min(indices)



def search_bracket(string: str, pos: int, direction: int, curly_bracket: bool=False) -> int:
    """
    searches the corresponding opening or closing bracket

    Parameters
    ----------
    string : str
        A formula.
    pos : int
        The Index of the bracket, at which searching should be started.
    direction : int
        The direction at which should be searched.

    Returns
    -------
    int
        Index of the corresponding bracket.

    """
    if curly_bracket:
        opening, closing = "{", "}"
    else:
        opening, closing = "(", ")"
        
    numcorr, numdiff = 0, 0
    
    if direction == -1:
        while True:
            index = string.rfind(opening, 0, pos)
            # if index == -1:
            #     raise Exception
            numdiff += string.count(closing, index, pos)
            
            if numdiff == numcorr:
                return index
            numcorr += 1
            pos = index
                
    elif direction == 1:
        pos += 1
        while True:
            index = string.find(closing, pos)
            numdiff += string.count(opening, pos, index)
            
            if numdiff == numcorr:
                return index
            numcorr += 1
            pos = index + 1

