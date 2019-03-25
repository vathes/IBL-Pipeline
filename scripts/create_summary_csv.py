'''
This script creates a summary of the training status of animals in each lab.
'''

import datajoint as dj
from ibl_pipeline import reference, subject, action, acquisition, behavior
from ibl_pipeline.analyses import behavior as behavior_analyses
import pandas as pd
import numpy as np
from datetime import datetime


for ilab in reference.Lab:
    ingested_sessions = acquisition.Session & 'task_protocol!="NULL"' \
        & behavior.TrialSet
    subjects = ((subject.Subject & ilab) - subject.Death) & 'sex != "U"' & \
        action.Weighing & action.WaterAdministration & ingested_sessions

    if not len(subjects):
        continue

    last_sessions = subjects.aggr(
        ingested_sessions,
        session_start_time='max(session_start_time)') \
        * acquisition.Session \
        * behavior_analyses.SessionTrainingStatus
    summary = last_sessions.fetch(as_dict=True)

    task_protocols = last_sessions.fetch('task_protocol')
    protocols = [protocol.partition('ChoiceWorld')[0]
                 for protocol in task_protocols]
    for i, entry in enumerate(summary):
        subj = subject.Subject & entry
        protocol = protocols[i]
        entry['last_session_start_time'] = entry.pop('session_start_time')
        entry['current_task_protocol'] = entry.pop('task_protocol')
        entry['current_training_status'] = entry.pop('training_status')
        # get all sessions with this protocol
        entry['n_sessions'] = len(
            ingested_sessions & subj &
            'task_protocol LIKE "{}%"'.format(protocol))

    summary = pd.DataFrame(summary)
    summary.pop('lab_name')
    summary.index += 1
    last_session_date = \
        np.max(summary['last_session_start_time']).date().strftime('%Y-%m-%d')
    summary.to_csv(
        '/src/IBL-pipeline/snapshots/{}_{}_summary.csv'.format(
            last_session_date, ilab['lab_name']))
    print('Saved {} current training status summary.'.format(ilab['lab_name']))