import logging
from apscheduler.scheduler import Scheduler as ApScheduler
from core.updater import Updater, UPDATE_ALL
from core.downloaders import Downloader
from core.config import configmanager

log = logging.getLogger(__name__)
sched = ApScheduler()

@sched.cron_schedule(hour = configmanager.get('scheduler', 'hour'), \
    minute = configmanager.get('scheduler', 'minute'))
def update_and_download():
    log.debug('Update and download job started...')
    updater = Updater()
    updater.update(UPDATE_ALL)
    
    downloader = Downloader()
    downloader.download_wanted_shows()
    log.debug('Update and download job finished...')

class Scheduler(object):
    def start(self):
        sched.start()
        
        if configmanager.getboolean('scheduler', 'run_onstart'):
            update_and_download()