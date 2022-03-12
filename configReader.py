import json
from pprint import pprint
from os.path import join

class ConfigReader:
    def __init__(self, pathToConfig='.'):
        with open(join(pathToConfig, 'config.json'), 'r', encoding='utf-8') as f:
            self.config = json.load(f)
    
    def getConfig(self):
        return self.config

if __name__ == '__main__':
    cr = ConfigReader()
