import cherrypy
import logging
from root import Root
from show import Show
from tools.common import get_absolute_path
from core.scheduler import Scheduler

log = logging.getLogger(__name__)

class DramastarServer:
    config = None
    
    def __init__(self):
        static_dir = get_absolute_path('web/static')        
        self.config = { 
            '/static': {
                'tools.gzip.on': True, 
                'tools.staticdir.on': True,
                'tools.staticdir.dir': static_dir
            },
            '/': {
                'request.dispatch': self.setup_routes()
            }
        }
        
    def start(self):
        cherrypy.config['tools.encode.on'] = True
        cherrypy.config['tools.encode.encoding'] = 'utf-8'
        cherrypy.config['tools.sessions.on'] = True
        cherrypy.config['server.environment'] = 'production'
        cherrypy.config['engine.autoreload_on'] = True
        cherrypy.config['engine.autoreload_frequency'] = 5
        
        configfile = get_absolute_path('web.ini')
        cherrypy.config.update(configfile)
        cherrypy.config.update(self.config)
        
        app = cherrypy.tree.mount(root = None, config = configfile)
        app.merge(self.config)
        
        cherrypy.engine.autoreload.files.add(get_absolute_path('core.ini'))
        cherrypy.engine.start()
        log.info('Server started...')
        
        # Start snatch scheduler
        scheduler = Scheduler()
        scheduler.start()
        
        cherrypy.engine.block()

    def setup_routes(self):
        root = Root()
        show = Show()
        # Create an instance of the dispatcher
        route_mapper = cherrypy.dispatch.RoutesDispatcher()
        # connect a route that will be handled by the 'index' handler
        route_mapper.connect('home', '/', controller = root, action = 'index')
        route_mapper.connect('manage', '/manage', controller = root, \
            action = 'manage')
        route_mapper.connect('settings', '/settings', controller = root, \
            action = 'settings')
        route_mapper.connect('update', '/update', controller = show, \
            action = 'update')
        route_mapper.connect('update', '/update/wanted', controller = show, \
            action = 'update_wanted')
        route_mapper.connect('update', R'/update/{show_id:\d+}', 
            controller = show, action = 'update')
        route_mapper.connect('show', R'/show/{show_id:\d+}', 
            controller = show, action = 'index')
        route_mapper.connect('want', R'/show/{show_id:\d+}/want', 
            controller = show, action = 'want')
        route_mapper.connect('unwant', R'/show/{show_id:\d+}/unwant', 
            controller = show, action = 'unwant')
        route_mapper.connect('show_episodes', R'/show/{show_id:\d+}/episodes', 
            controller = show, action = 'show_episodes')
        route_mapper.connect('latest_episodes', '/episodes/latest', \
            controller = show, action = 'latest_episodes')
        route_mapper.connect('download', R'/episode/{episode_id:\d+}/download', 
            controller = show, action = 'download')
        route_mapper.connect('download', '/shows/wanted/download', \
            controller = show, action = 'download_wanted_shows')
            
        return route_mapper