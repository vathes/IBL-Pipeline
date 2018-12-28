#! /usr/bin/env python3

import os
import sys
import logging


from code import interact

# BOOKMARK: ensure loading
from ibl_pipeline import reference
from ibl_pipeline import subject
from ibl_pipeline import acquisition
from ibl_pipeline import behavior
from ibl_pipeline import ephys


log = logging.getLogger(__name__)
__all__ = [reference, subject, acquisition, behavior, ephys]


def usage_exit():
    print("usage: {p} [{c}]"
          .format(p=os.path.basename(sys.argv[0]),
                  c='|'.join(list(actions.keys()))))
    sys.exit(0)


def logsetup(*args):
    logging.basicConfig(level=logging.ERROR)
    log.setLevel(logging.DEBUG)
    logging.getLogger('ibl').setLevel(logging.DEBUG)
    logging.getLogger('ibl.ingest').setLevel(logging.DEBUG)


def cmd_shell(*args):
    return interact('ibl shell.\n\nschema modules:\n\n  - {m}\n'
             .format(m='\n  - '.join(
                 '.'.join(m.__name__.split('.')[1:]) for m in __all__)),
             local=globals())


def cmd_ingest(*args):
    scripts = os.path.dirname(__file__)
    return os.system(os.path.join(scripts, 'ingest_all.sh'))


if __name__ == '__main__':

    actions = {
        'shell': cmd_shell,
        'ingest': cmd_ingest,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in actions:
        usage_exit()

    logsetup()

    action = sys.argv[1]
    actions[action](sys.argv[2:])
