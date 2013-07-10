
class BaseDownloader(object):
    name = None
    id = None
    active = False
    use_for = []
    
    def download(self, url):
        pass