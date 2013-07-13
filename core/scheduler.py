from apscheduler.scheduler import Scheduler as ApScheduler
from core.updater import Updater, UPDATE_ALL
from core.downloaders import Downloader
from core.config import configmanager

sched = ApScheduler()

@sched.cron_schedule(hour = configmanager.get('scheduler', 'hour'), \
    minute = configmanager.get('scheduler', 'minute'))
def update_and_download():
    print "Updating..."
    updater = Updater()
    updater.update(UPDATE_ALL)
    
    downloader = Downloader()
    print "Downloading..."
    downloader.download_wanted_shows()
    print "Finished..."

class Scheduler(object):
    def start(self):
        sched.start()
        
        if configmanager.getboolean('scheduler', 'run_onstart'):
            update_and_download()