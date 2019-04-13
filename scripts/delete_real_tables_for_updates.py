
import datajoint as dj
from ibl_pipeline import action, subject
from ibl_pipeline.ingest import action as action_ingest
from ibl_pipeline.ingest import subject as subject_ingest


dj.config['safemode'] = False

# delete some real tables when the shadow tables are available

if len(subject_ingest.SubjectUser()):
    subject.SubjectUser.delete()

if len(subject_ingest.SubjectLab()):
    subject.SubjectLab.delete()

if len(action_ingest.Weighing()):
    action.Weighing.delete()

if len(action_ingest.WaterAdministration()):
    action.WaterAdministration.delete()

if len(action_ingest.WaterRestriction()):
    action.WaterRestriction.delete()
