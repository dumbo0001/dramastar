import cherrypy
import json
from tools.common import render_template
from core.downloaders import Downloader
from core.updater import Updater, UPDATE_SHOWS_ONLY
from core.repositories.shows import ShowRepository
from core.repositories.episodes import EpisodeRepository

class Show:
    show_repository = ShowRepository()
    episode_repository = EpisodeRepository()
    
    def index(self, show_id):
        show = self.show_repository.get_show(show_id)
        return render_template('show.html',
            episode_list = dict(episodes = self.episode_repository \
                .get_show_episodes(show), title = show.name, mode = 'all', \
                show_id = show.id)
        )
    
    @cherrypy.tools.allow(methods=['POST'])
    def update(self, show_id = -1):
        updater = Updater()
        if show_id == -1:
            updater.update(UPDATE_SHOWS_ONLY)
            shows = self.show_repository.get_manageable_shows()
            return json.dumps({
                'fragments' : {
                    '#available-shows': render_template('available-shows.html', 
                        shows = shows)
                }
            })
        else:
            updater.update_show(show_id)   
            wanted = self.show_repository.get_show(show_id)
            return json.dumps({
                'html' : render_template('wanted.html',
                    show = wanted)
            })
    
    @cherrypy.tools.allow(methods=['POST'])
    def want(self, show_id):
        return self.update_wanted_and_refresh(show_id, True)
        
    @cherrypy.tools.allow(methods=['POST'])
    def unwant(self, show_id):
        return self.update_wanted_and_refresh(show_id, False)
        
    def update_wanted_and_refresh(self, show_id, wanted_status):
        show = self.show_repository.get_show(show_id)
        show.wanted = wanted_status
        self.show_repository.save_show(show)
        wanted = self.show_repository.get_wanted_shows()
        episodes = self.episode_repository.get_latest_episodes()
        return json.dumps({
            'fragments' : {
                '#wanted-shows': render_template('wanted-shows.html', 
                    wanted = wanted),
                '#available-btn-group-%s' % show_id: 
                    render_template('shows-btn-group.html', show = show),
                '#episodes-list': render_template('episodes.html',
                    episode_list = dict(episodes = episodes, 
                    title = "Latest episodes", 
                    mode = 'latest', show_id = -1))
            }
        })
    
    def latest_episodes(self):
        episodes = self.episode_repository.get_latest_episodes()
        return json.dumps({
            'html': render_template('episodes.html',
                episode_list = dict(episodes = episodes, \
                    title = "Latest episodes", mode = 'latest'))
        })
        
    def show_episodes(self, show_id):
        show = self.show_repository.get_show(show_id)
        episodes = self.episode_repository.get_show_episodes(show)
        return json.dumps({
            'html': render_template('episodes.html', \
                episode_list = dict(episodes = episodes, title = show.name, \
                    mode = 'all', show_id = show_id))
        })
        
    def download(self, episode_id):
        downloader = Downloader()
        downloader.download(episode_id)
        episode = self.episode_repository.get_episode(episode_id)
        return json.dumps({
                'html' : render_template('episode-row.html', episode = episode)
            })