import os
import yaml

class Config:
    '''Parameters to call user-defined functions'''

    PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..', 'config.yaml')

    def __init__(self, config : dict) -> None:
        self.minimal_voltage_search = config['minimal_voltage_search']
        self.normal_speed_interval = config['normal_speed_interval']
        self.normal_voltage_interval = config['normal_voltage_interval']

    def save(self) -> None:
        '''Write all available parameters in the document (rewrite)'''
        config = {
            'minimal_voltage_search': self.minimal_voltage_search,
            'normal_speed_interval': self.normal_speed_interval,
            'normal_voltage_interval': self.normal_voltage_interval
        }

        with open(Config.PATH, 'w', encoding='UTF-8') as file_write:
            yaml.dump(config, file_write, default_flow_style=False)

    @classmethod
    def create_initial(cls):
        '''Create config with initial settings'''
        config = cls({
            'minimal_voltage_search': 12,
            'normal_speed_interval': {
                'min': 0,
                'max': 80
            },
            'normal_voltage_interval': {
                'min': 0,
                'max': 60
            }})
        return config

    @classmethod
    def collect(cls):
        '''Collecting config options'''
        try:
            with open(Config.PATH, 'r', encoding='UTF-8') as file_read:
                config = cls(yaml.safe_load(file_read))
        except (KeyError, FileNotFoundError):
            config = Config.create_initial()
            config.save()

        return config
