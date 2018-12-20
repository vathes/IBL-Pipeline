#! /bin/sh

host=http://ibl.flatironinstitute.org
path=json/alyxfull.json.gz

cd `basename $0`/.. \
	&& curl -O --netrc-optional=./.netrc ${host}/${path}
