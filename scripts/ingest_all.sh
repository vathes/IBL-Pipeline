#! /bin/sh
cd `dirname $0` \
&& ./fetch_json.sh \
&& ./delete_shadow_tables_for_updates.py \
&& ./ingest_alyx_raw.py "$@" \
&& ./ingest_alyx_shadow.py \
&& ./ingest_alyx_shadow_membership.py \
&& ./delete_real_tables_for_updates.py \
&& ./ingest_alyx_real.py \
&& ./ingest_behavior.py \
&& cd ../prelim_analyses/behavioral_snapshots \
&& ./behavioral_snapshot.py \
&& ./behavioral_overview_perlab.py
