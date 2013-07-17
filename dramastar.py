import logging
import logging.config
import sys
from tools.common import get_absolute_path
from web import DramastarServer

logging.config.fileConfig(get_absolute_path('core.ini'), disable_existing_loggers=False)
log = logging.getLogger('dramastar')

def main():
    try:
        web_server = DramastarServer()
        web_server.start()
    except Exception, e:
        # Dump callstack to log and exit with -1
        log.exception('Unexpected exception occured.')
        raise e

if __name__ == '__main__':
    sys.exit(main())