# coding=utf-8
import logging
import warnings

from collections import OrderedDict
from datetime import datetime
from pathlib import Path

import yaml
import matplotlib
matplotlib.use("Agg") # disable rocket launcher in OSX
# noinspection PyUnresolvedReferences
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import pandas_profiling as pp

from saapy.vcs import GitClient


class Toolbox:
    data = None
    cfg = None
    secret_cfg = None

    def __init__(self, cfg_yaml=None, secret_cfg_yaml=None,
                 create_vcs_client=True):
        self.data = OrderedDict()
        self.cfg_yaml = cfg_yaml
        self.secret_cfg_yaml = secret_cfg_yaml
        if cfg_yaml and Path(cfg_yaml).exists():
            self.cfg = self.load_cfg(cfg_yaml)
        else:
            self.cfg = {}
        if secret_cfg_yaml and Path(secret_cfg_yaml).exists():
            self.secret_cfg = self.load_cfg(secret_cfg_yaml)
        else:
            self.secret_cfg = {}
        self._ensure_cfg_structure()
        if create_vcs_client:
            self._create_vcs_client()

    def _ensure_cfg_structure(self):
        self.cfg.setdefault('save_stamp', None)
        self.cfg.setdefault('codebase', dict(directory=None, vcs=None))
        self.cfg.setdefault('matplotlib', dict(notebook={
            'lines.linewidth': 2.5,
            'figure.figsize': (16, 6)
        }))
        self.cfg.setdefault('data', dict(frames={}))

    def _create_vcs_client(self):
        if (self.cfg['codebase']['vcs'] == 'git'
            and self.cfg['codebase']['directory']):
            self.git_client = GitClient(self.cfg['codebase']['directory'])

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
        if persist_feather and isinstance(persist_feather, str):
            frame_feather = persist_feather
        elif persist_feather:
            frame_feather = '{}.feather'.format(key)
        else:
            frame_feather = None
        self.data[key] = df
        if frame_feather:
            self.cfg['data']['frames'][key] = frame_feather

    def save_frame(self, key, df=None, persist_feather=None):
        if df:
            self.data[key] = df
        if persist_feather:
            self.cfg['data']['frames'][key] = persist_feather
        self.data[key].to_feather(self.cfg['data']['frames'][key])

    def load_frame(self, key, persist_feather=None):
        if persist_feather:
            self.cfg['data']['frames'][key] = persist_feather
        df = pd.read_feather(self.cfg['data']['frames'][key])
        self.data[key] = df
        return df

    def load_all_frames(self):
        return [self.load_frame(key) for key in self.cfg['data']['frames']]

    def add_codebase_path(self, dir, vcs='git'):
        self.cfg['codebase']['directory'] = dir
        self.cfg['codebase']['vcs'] = vcs
        self._create_vcs_client()

    def extract_commit_history(self):
        pass

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
