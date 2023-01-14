'''Functions and classes for manipulating the text displayed in the terminal'''

from colorama import Fore, Style

class Color:
    '''Functionality related to text coloring'''
    @staticmethod
    def cprint(msg : str, fore="", back="", style="", end="") -> None:
        '''Color and print text in the terminal'''
        print(Color.colorize(msg, fore, back, style), end=end)

    @staticmethod
    def colorize(msg : str, fore="", back="", style="") -> str:
        '''Color text in the terminal'''
        return f"{fore}{back}{style}{msg}{Style.RESET_ALL}"

class ConstantValueOutput:
    '''Storing information to output a constant value'''
    def __init__(self, description : str, value : str) -> None:
        self.description = description
        self.value = value
        
    def display(self) -> None:
        '''Outputs the value with its description'''
        description_colored = Color.colorize(msg=self.description, fore=Fore.WHITE, style=Style.BRIGHT)
        value_colored = Color.colorize(msg=self.value, fore=Fore.CYAN, style=Style.BRIGHT)
        print(f"{description_colored}: {value_colored}")

class CalculatedValueOutput(ConstantValueOutput):
    '''Storing information for the output of a single calculated value'''
    def __init__(self, description : str, value : str, units_of_measure : str) -> None:
        super().__init__(description, value)
        self.units_of_measure = units_of_measure
    
    def display(self, value_estimation=True) -> None:
        '''Outputs the value with its description and units'''
        value_color = Fore.GREEN if not value_estimation else (Fore.GREEN if float(self.value) > 0 else (Fore.YELLOW if float(self.value) == 0 else Fore.RED))

        description_colored = Color.colorize(msg=self.description, fore=Fore.WHITE, style=Style.BRIGHT)
        value_colored = Color.colorize(msg=self.value, fore=value_color, style=Style.BRIGHT)
        units_of_measure_colored = Color.colorize(msg=self.units_of_measure, fore=Fore.WHITE, style=Style.BRIGHT)

        print(f"{description_colored}: {value_colored} {units_of_measure_colored}")

