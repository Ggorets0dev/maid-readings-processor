import os
import yaml

class Config:
    '''Parameters to call user-defined functions'''

    PATH = os.path.join(os.path.split(os.path.abspath(__file__))[0], '..', 'config.yaml')

    def __init__(self, config : dict) -> None:
        self.minimal_voltage = config['minimal_voltage']
        self.maximal_speed = config['maximal_speed']

    def save(self) -> None:
        '''Write all available parameters in the document (rewrite)'''
        config = {
            'minimal_voltage': self.minimal_voltage,
            'maximal_speed': self.maximal_speed
        }

        with open(Config.PATH, 'w', encoding='UTF-8') as file_write:
            yaml.dump(config, file_write, default_flow_style=False)

    @classmethod
    def create_initial(cls):
        '''Create config with initial settings'''
        config = cls({
            'minimal_voltage': 12,
            'maximal_speed': 80})
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
