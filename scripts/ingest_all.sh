#! /bin/sh
cd `dirname $0` \
&& ./fetch_json.sh \
&& ./ingest_alyx_raw.py "$@" \
&& ./ingest_alyx_shadow.py \
&& ./ingest_alyx_shadow_membership.py \
&& ./ingest_alyx_real.py \
&& ./ingest_behavior.py \
&& cd ../prelim_analyses/behavioral_snapshots \
&& ./behavioral_snapshot.py \
&& ./behavioral_overview_perlab.py
