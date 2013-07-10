from apscheduler.scheduler import Scheduler as ApScheduler
from core.repositories.shows import ShowRepository
from core.updater import Updater, UPDATE_ALL
from core.downloaders import Downloader
from core.entities.models import EPISODE_STATUS_WANTED
from core.config import configmanager

sched = ApScheduler()

@sched.cron_schedule(hour = configmanager.get('scheduler', 'hour'), \
    minute = configmanager.get('scheduler', 'minute'))
def update_and_download():
    print "Updating..."
    updater = Updater()
    updater.update(UPDATE_ALL)
    
    downloader = Downloader()
    show_repository = ShowRepository()
    wanted_shows = show_repository.get_wanted_shows()
    print "Downloading..."
    for show in wanted_shows:
        wanted_episodes = show.episodes.filter_by(status = \
            EPISODE_STATUS_WANTED)
        for episode in wanted_episodes:
            downloader.download(episode.id)
    print "Finished..."

class Scheduler(object):
    def start(self):
        sched.start()
        
        if configmanager.getboolean('scheduler', 'run_onstart'):
            update_and_download()