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
# configuration:
#
#   The jobs expect:
# 
#   - a properly configured dj_local_conf.json in the checkout root to
#     authenticate to the database
#
#   - a properly configured netrc(5) file in the checkout root to authenticate 
#     the fetch of raw json data, if applicable. 
#
#     for reference, netrc file format is as follows:
#
#       machine FQDNORIP login LOGINNAME password PASSWORD
#

host=http://ibl.flatironinstitute.org
path=json/alyxfull.json.gz
log=/tmp/datajoint-ingest.log

dosetup(){ crontab ${0%%.sh}; }

dorun() {
	( cd `dirname $0`/.. \
		&& echo "# fetching at `date`" \
			curl -O --netrc-optional=./.netrc ${host}/${path}
				) >> $log 2>&1

	( cd `dirname $0`/.. \
		&& echo "# running at `date`" \
		&& docker-compose \
			-f docker-compose.yml up \
			datajoint-ingest \
				) >> $log 2>&1
}

# _start:
[ "$1" = "install" ] && dosetup || dorun
