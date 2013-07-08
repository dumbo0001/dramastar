import sys
import logging 

from web import DramastarServer

log = logging.getLogger(__name__)

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