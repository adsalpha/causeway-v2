import json
import config

class Template:

    def __init__(self, template_name):
        self.template_file = json.loads(open(config.template_dir + '/' + template_name + '.json', 'r').read())

    def populate(self, **kwargs):
        template = json.loads(self.template_file)
        for key, value in kwargs.items():
            template[key] = value
