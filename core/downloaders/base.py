
class BaseDownloader(object):
    name = None
    id = None
    active = False
    use_for = []
    config = []
    
    def _get_config(self, option_name):
        value = None
        options = self.config['options']
        if any(x['name'] == option_name for x in options):
            option =  next(x for x in options if x['name'] == option_name)
            if 'default' in option:
                value = option['default']
            if 'value' in option:
                value = option['value']
        
        return value
    
    def download(self, url):
        pass