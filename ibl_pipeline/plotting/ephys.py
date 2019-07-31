import datajoint as dj
from .. import behavior, ephys
from . import plotting_utils_ephys as putils
import numpy as np
import pandas as pd
import plotly
import plotly.graph_objs as go
import json

schema = dj.schema(dj.config.get('database.prefix', '') +
                   'ibl_plotting_ephys')


@schema
class Sorting(dj.Lookup):
    definition = """
    sort_by:     varchar(32)
    """
    contents = zip(['trial_id',
                    'response - stim on',
                    'feedback - stim on',
                    'feedback - response'])


@schema
class ValidAlignSort(dj.Lookup):
    definition = """
    -> ephys.Event
    -> Sorting
    """
    contents = [
        ['stim on', 'trial_id'],
        ['stim on', 'response - stim on'],
        ['stim on', 'feedback - stim on'],
        ['response', 'trial_id'],
        ['response', 'response - stim on'],
        ['response', 'feedback - response'],
        ['feedback', 'trial_id'],
        ['feedback', 'feedback - stim on'],
        ['feedback', 'feedback - response']
    ]


@schema
class TrialCondition(dj.Lookup):
    definition = """
    trial_condition:  varchar(32)
    """

    contents = zip(['all trials',
                    'correct trials',
                    'left trials',
                    'right trials'])


@schema
class Raster(dj.Computed):
    definition = """
    -> ephys.Cluster
    -> ValidAlignSort
    ---
    plotting_data:      blob@plotting
    """

    def make(self, key):
        cluster = ephys.Cluster & key
        trials = \
            (behavior.TrialSet.Trial * ephys.TrialSpikes & cluster).proj(
                'trial_start_time', 'trial_stim_on_time',
                'trial_response_time',
                'trial_feedback_time',
                'trial_response_choice',
                'trial_spike_times',
                trial_duration='trial_end_time-trial_start_time',
                trial_signed_contrast="""trial_stim_contrast_right -
                                         trial_stim_contrast_left"""
            ) & 'trial_duration < 5' & 'trial_response_choice!="No Go"'

        if not len(trials):
            return
        align_event = (ephys.Event & key).fetch1('event')
        sorting_var = (Sorting & key).fetch1('sort_by')
        x_lim = [-1, 1]
        encoded_string, y_lim, label = putils.create_raster_plot_combined(
            trials, align_event, sorting_var)

        axis = go.Scatter(
            x=x_lim,
            y=y_lim,
            mode='markers',
            marker=dict(opacity=0),
            showlegend=False
        )

        legend_left = putils.get_legend('left', 'spike')
        legend_right = putils.get_legend('right', 'spike')
        legend_incorrect = putils.get_legend('incorrect', 'spike')

        legend_mark_left = putils.get_legend('left', label)
        legend_mark_right = putils.get_legend('right', label)
        legend_mark_incorrect = putils.get_legend('incorrect', label)

        layout = go.Layout(
            images=[dict(
                source='data:image/png;base64, ' + encoded_string.decode(),
                sizex=x_lim[1] - x_lim[0],
                sizey=y_lim[1] - y_lim[0],
                x=x_lim[0],
                y=y_lim[1],
                xref='x',
                yref='y',
                sizing='stretch',
                layer='below'
                )],
            width=580,
            height=370,
            margin=go.layout.Margin(
                l=50,
                r=30,
                b=40,
                t=80,
                pad=0
            ),
            title=dict(
                text='Raster, aligned to {}'.format(align_event),
                x=0.21,
                y=0.87
            ),
            xaxis=dict(
                title='Time (sec)',
                range=x_lim,
                showgrid=False
            ),
            yaxis=dict(
                title='Trial idx',
                range=y_lim,
                showgrid=False
            ),
        #     template=dict(
        #         layout=dict(
        #             plot_bgcolor="#fff"
        #         )
        #     )
        )

        data = [axis, legend_left, legend_right, legend_incorrect,
                legend_mark_left, legend_mark_right, legend_mark_incorrect]

        fig = go.Figure(data=data, layout=layout)
        key['plotting_data'] = fig.to_plotly_json()
        self.insert1(key)


@schema
class Psth(dj.Computed):
    definition = """
    -> ephys.Cluster
    -> ephys.Event
    ---
    plotting_data:       blob@plotting
    """
    key_source = ephys.Cluster * (ephys.Event & 'event != "go cue"')

    def make(self, key):
        cluster = ephys.Cluster & key
        trials_all = (behavior.TrialSet.Trial * ephys.TrialSpikes & cluster).proj(
            'trial_start_time', 'trial_stim_on_time',
            'trial_response_time', 'trial_feedback_time',
            'trial_response_choice', 'trial_spike_times',
            trial_duration='trial_end_time-trial_start_time',
            trial_signed_contrast='trial_stim_contrast_right - trial_stim_contrast_left'
        ) & 'trial_duration < 5' & 'trial_response_choice!="No Go"' & key

        trials_left = trials_all & 'trial_response_choice="CW"' \
            & 'trial_signed_contrast < 0'
        trials_right = trials_all & 'trial_response_choice="CCW"' \
            & 'trial_signed_contrast > 0'
        trials_incorrect = trials_all - \
            trials_right.proj() - trials_left.proj()

        align_event = (ephys.Event & key).fetch1('event')
        x_lim = [-1, 1]
        data = []
        if len(trials_left):
            data.append(
                putils.compute_psth(
                    trials_left, 'left', align_event, 1000, 10, x_lim)
            )
        if len(trials_right):
            data.append(
                putils.compute_psth(
                    trials_right, 'right', align_event, 1000, 10, x_lim)
            )
        if len(trials_incorrect):
            data.append(
                putils.compute_psth(
                    trials_incorrect, 'incorrect', align_event, 1000, 10, x_lim)
            )

        data.append(
            putils.compute_psth(
                trials_all, 'all', align_event, 1000, 10, x_lim)
        )

        layout = go.Layout(
            width=580,
            height=370,
            margin=go.layout.Margin(
                l=50,
                r=30,
                b=40,
                t=80,
                pad=0
            ),
            title=dict(
                text='PSTH, aligned to {} time'.format(align_event),
                x=0.2,
                y=0.87
            ),
            xaxis=dict(
                title='Time (sec)',
                range=x_lim,
                showgrid=False
            ),
            yaxis=dict(
                title='Firing rate (spks/sec)',
                showgrid=False
            ),
        )

        fig = go.Figure(data=data, layout=layout)
        key['plotting_data'] = fig.to_plotly_json()
        self.insert1(key)