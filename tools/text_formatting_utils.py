'''Functions for manipulating the text displayed in the terminal'''

from colorama import Style

def cprint(msg : str, fore="", back="", style="") -> None:
    '''Color and print text in the terminal'''
    print(colorize(msg, fore, back, style))

def colorize(msg : str, fore="", back="", style="") -> str:
    '''Color text in the terminal'''
    return f"{fore}{back}{style}{msg}{Style.RESET_ALL}"
