#! /bin/sh

# scripts/datajoint-ingest.cron.sh: driver for datajoint-ingest container
#
# usage:
# 
#   $ datajoint-ingest.cron.sh 
#
#     run the ingest job container
#
#   $ datajoint-ingest.cron.sh install
#
#     replaces current user crontab with cronjob to run this script
#

dosetup(){ crontab ${0%%.sh}; }

dorun() {
	( cd `dirname $0`/.. \
		&& echo "# running at `date`" \
		&& docker-compose \
			-f docker-compose.yml up \
			datajoint-ingest \
				) >> /tmp/datajoint-ingest.log 2>&1
}

# _start:
[ "$1" = "install" ] && dosetup || dorun
