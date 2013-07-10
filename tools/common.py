import os, sys, logging
import platform
import cherrypy

import jinja2.ext
from jinja2 import Environment, PackageLoader
      
def get_absolute_path(filename):
    if getattr(sys, 'frozen', False):
        # The application is frozen
        pathname = os.path.dirname(sys.executable)
    else:
        # The application is not frozen
        # Change this bit to match where you store your data files:
        pathname = os.path.abspath('')

    return os.path.join(pathname, filename)
    
template_dir = get_absolute_path('web/templates')
loader = jinja2.FileSystemLoader(template_dir)
jinja_env = jinja2.Environment(loader=loader)
log = logging.getLogger(__name__)
    
class FlashMessage(object):
    def __init__(self, message, level):
        self.message = message
        self.level = level

    def __repr__(self):
        return self.message
    
class FlashMessagesIterator(object):
    def __init__(self):
        self.messages = list()

    def append(self, message):
        self.messages.append(message)

    def __iter__(self):
        return self

    def next(self):
        if len(self.messages):
            return self.messages.pop(0)
        else:
            raise StopIteration
    
def flash(message, level='info'):    
    if 'flash' not in cherrypy.session:
         cherrypy.session['flash'] = FlashMessagesIterator()

    if not level in ['info', 'error', 'warning', 'success']:
        log.warning("Got flash message '%s' with invalid message level: '%" + \
            "s'", message, level)
        level = 'info'

    flash_message = FlashMessage(message, level)
    cherrypy.session['flash'].append(flash_message)
    
def info(message):
    flash(message, 'info')

def error(message):
    flash(message, 'error')

def warning(message):
    flash(message, 'warning')

def success(message):
    flash(message, 'success')
    
def get_messages():
    if 'flash' in cherrypy.session:
        return cherrypy.session['flash']
    else:
        return list()
        
def render_template(template, **kwargs):
    kwargs['messages'] = get_messages()
    return jinja_env.get_template(template).render(**kwargs)

def getUserDir():
    try:
        import pwd
        os.environ['HOME'] = pwd.getpwuid(os.geteuid()).pw_dir
    except:
        pass

    return os.path.expanduser('~')
