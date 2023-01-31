from dataclasses import dataclass, field

@dataclass
class BarGraphConfig:
    '''Storing data about the future graph'''
    values_x: list = field(default_factory=list)
    values_y: list = field(default_factory=list)
    label_x: str = 'X axis'
    label_y: str = 'Y axis'
    label_fig: str = "Graph with the X and Y axes"
