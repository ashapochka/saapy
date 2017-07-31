# coding=utf-8
import logging
import warnings

from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import yaml
import matplotlib
matplotlib.use("Agg")  # disable rocket launcher in OSX
# noinspection PyUnresolvedReferences
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pandas_profiling as pp

from saapy.vcs import GitClient
from .actor import connect_actors, combine_actors


class Toolbox:
    data = None
    cfg = None
    secret_cfg = None
    vcs_client = None

    def __init__(self, cfg_yaml=None, secret_cfg_yaml=None,
                 create_vcs_client=True,
                 load_cfg=True, load_secret_cfg=True,
                 default_data_directory=None,
                 create_default_data_directory=True):
        self.data = OrderedDict()
        self.cfg_yaml = cfg_yaml
        self.secret_cfg_yaml = secret_cfg_yaml
        if load_cfg and cfg_yaml and Path(cfg_yaml).exists():
            self.cfg = self.load_cfg(cfg_yaml)
        else:
            self.cfg = {}
        if (load_secret_cfg and secret_cfg_yaml
            and Path(secret_cfg_yaml).exists()):
            self.secret_cfg = self.load_cfg(secret_cfg_yaml)
        else:
            self.secret_cfg = {}
        self._ensure_cfg_structure()
        if create_vcs_client:
            self._create_vcs_client()
        if default_data_directory:
            self.set_default_data_directory(
                default_data_directory, create=create_default_data_directory)

    @property
    def default_data_directory(self):
        return Path(self.cfg['default_data_directory'] or '.')

    def set_default_data_directory(self, default_data_directory, create=True):
        self.cfg['default_data_directory'] = str(default_data_directory)
        if create:
            Path(default_data_directory).mkdir(parents=True, exist_ok=True)

    def _ensure_cfg_structure(self):
        self.cfg.setdefault('save_stamp', datetime.utcnow())
        self.cfg.setdefault('codebase', dict(directory=None, vcs=None))
        self.cfg.setdefault('matplotlib', dict(notebook={
            'lines.linewidth': 2.5,
            'figure.figsize': (16, 6)
        }))
        self.cfg.setdefault('data', dict(frames={}))
        self.cfg.setdefault('default_data_directory', '.')

    def _create_vcs_client(self):
        if (self.cfg['codebase']['vcs'] == 'git'
            and self.cfg['codebase']['directory']):
            self.vcs_client = GitClient(self.cfg['codebase']['directory'])

    @staticmethod
    def load_cfg(cfg_yaml):
        with open(cfg_yaml) as yaml_file:
            return yaml.load(yaml_file)

    def save_cfg(self):
        self.cfg['save_stamp'] = datetime.utcnow()
        with open(self.cfg_yaml, 'w') as yaml_file:
            yaml.dump(self.cfg, yaml_file,
                      default_flow_style=False)

    def add_frame(self, key, df, persist_feather=True):
        frame_feather = self.to_frame_feather_path(key, persist_feather)
        self.data[key] = df
        if frame_feather:
            self.cfg['data']['frames'][key] = frame_feather

    def to_frame_feather_path(self, key, persist_feather):
        if persist_feather:
            if isinstance(persist_feather, (str, Path)):
                frame_feather = str(persist_feather)
            else:
                file_name = '{}.feather'.format(key)
                frame_feather = str(self.default_data_directory / file_name)
        else:
            frame_feather = None
        return frame_feather

    def save_frame(self, key, df=None, persist_feather=None):
        if df is not None:
            self.data[key] = df
        frame_feather = self.to_frame_feather_path(key, persist_feather)
        if frame_feather:
            self.cfg['data']['frames'][key] = frame_feather
        self.data[key].to_feather(self.cfg['data']['frames'][key])

    def load_frame(self, key, persist_feather=None):
        if persist_feather:
            self.cfg['data']['frames'][key] = persist_feather
        df = pd.read_feather(self.cfg['data']['frames'][key])
        self.data[key] = df
        return df

    def load_all_frames(self):
        return [self.load_frame(key) for key in self.cfg['data']['frames']]

    @property
    def codebase_directory(self):
        if self.cfg['codebase']['directory']:
            return Path(self.cfg['codebase']['directory'])
        else:
            return None

    def set_codebase_directory(self, codebase_root_directory, vcs='git'):
        self.cfg['codebase']['directory'] = codebase_root_directory
        self.cfg['codebase']['vcs'] = vcs
        self._create_vcs_client()

    def extract_commit_history(self,
                               persist=True,
                               revs='all_refs',
                               include_trees=True,
                               paths='',
                               **kwargs):
        commit_history = self.vcs_client.extract_commit_history(
            revs=revs, include_trees=include_trees, paths=paths, **kwargs)
        for key, df in commit_history.items():
            self.save_frame(key, df=df, persist_feather=persist)
        return set(commit_history.keys())

    def combine_authors(self,
                        connectivity_sets,
                        actor_frame_key='actor_frame',
                        connectivity_column='actor_id',
                        persist=True):
        actor_frame = self.data[actor_frame_key]
        actor_frame = connect_actors(actor_frame,
                                     connectivity_sets,
                                     connectivity_column=connectivity_column)
        unique_actor_frame = combine_actors(actor_frame, connectivity_column)
        self.save_frame(actor_frame_key, df=actor_frame,
                        persist_feather=persist)
        unique_actor_frame_key = 'unique_{}'.format(actor_frame_key)
        self.add_frame(unique_actor_frame_key, unique_actor_frame,
                       persist_feather=persist)
        return unique_actor_frame_key

    def style_matplotlib_for_notebook(self):
        sns.set_context("notebook",
                        rc=self.cfg['matplotlib']['notebook'])

    def profile_frame(self, df, profile_html=None):
        if isinstance(df, str):
            frame = self.data[df]
        elif isinstance(df, pd.DataFrame):
            frame = df
        else:
            frame = pd.DataFrame(df)
        report = pp.ProfileReport(frame)
        if profile_html:
            report.to_file(profile_html)
        return report

    @staticmethod
    def disable_warnings():
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=UserWarning)

    @staticmethod
    def capture_logging():
        # mostly warnings caused by self-signed certs
        logging.captureWarnings(True)

    def setup_notebook_friendly(self):
        self.capture_logging()
        self.disable_warnings()
        self.style_matplotlib_for_notebook()
