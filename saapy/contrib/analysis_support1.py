# coding=utf-8
import shelve
import warnings
from collections import OrderedDict
from functools import partial
from pathlib import Path

import logging
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sortedcontainers import SortedDict

from saapy.codetools import ScitoolsClient


logger = logging.getLogger(__name__)


# noinspection PyMissingOrEmptyDocstring
def parse_to_list(lstr: str):
    l = [p.strip("'") for p in lstr.strip("[]").split(", ")]
    return l


FILE_TYPES = OrderedDict([
    ('python', ('.py', '.pxi', '.pyx', '.pxd')), ('template', '.tmpl'),
    ('c', '.c'), ('config', '.cfg'), ('translate', '.po'),
    ('shell', '.sh'), ('make', 'Makefile'), ('archive', '.gz'),
    ('patch', '.patch'), ('vcs', ('/CVS/Root', '/svn')),
    ('doc', ('README', '.txt', '.rst')), ('cert', '.pem')])


# noinspection PyMissingOrEmptyDocstring
class Assessment:
    assessment_path: Path
    # prj1 specific paths
    prj1_root_path: Path
    prj1_tickets_csv_path: Path
    prj1_code_repo_path: Path
    prj1_udb_path: Path
    shelve_prj1_code_db_path: Path
    prj1_metrics_csv: Path
    # prj2 specific paths
    prj2_root_path: Path
    prj2_tickets_csv_path: Path
    prj2_code_repo_path: Path
    prj2_udb_path: Path
    shelve_prj2_code_db_path: Path
    prj2_metrics_csv: Path
    prj1_project_metrics_csv: Path
    prj2_project_metrics_csv: Path

    def __init__(self, root_path: Path):
        self.file_types = FILE_TYPES
        self.assessment_path = root_path
        # prj1
        self.prj1_root_path = root_path / 'prj1'
        self.prj1_tickets_csv_path = self.prj1_root_path / 'tickets_prj1-long.csv'
        self.prj1_code_repo_path = self.prj1_root_path / 'prj1_main'
        self.prj1_udb_path = self.assessment_path / 'prj1_main.udb'
        self.shelve_prj1_code_db_path = self.assessment_path / 'prj1_code.shelve'
        self.prj1_metrics_csv = self.assessment_path / 'prj1_main.csv'
        self.prj1_project_metrics_csv = self.assessment_path / \
                                       'prj1-project-stats.csv'
        self.prj1_scitools_client = ScitoolsClient(self.prj1_udb_path)
        # prj2
        self.prj2_root_path = root_path / 'prj2'
        self.prj2_tickets_csv_path = self.prj2_root_path / 'tickets_prj2-long.csv'
        self.prj2_code_repo_path = self.prj2_root_path / 'prj2_main'
        self.prj2_udb_path = self.assessment_path / 'prj2_main.udb'
        self.shelve_prj2_code_db_path = self.assessment_path / 'prj2_code.shelve'
        self.prj2_metrics_csv = self.assessment_path / 'prj2_main.csv'
        self.prj2_project_metrics_csv = self.assessment_path / \
                                       'prj2-project-stats.csv'
        self.prj2_scitools_client = ScitoolsClient(self.prj2_udb_path)

    # methods reusable between prj1 and prj2

    def load_project_metrics(self, path):
        return pd.read_csv(path)

    def load_tickets(self, path: Path) -> pd.DataFrame:
        return pd.read_csv(
            path,
            converters={'Changed files': parse_to_list},
            parse_dates=['CommitDate'])

    def collect_changed_files(self, ticket_frame: pd.DataFrame):
        changed_files = SortedDict()
        for i, files in enumerate(ticket_frame.ChangedFiles):
            for f in files:
                changed_files.setdefault(f, []).append(i)
        return changed_files

    def collect_source_files(self, code_repo_path):
        src_patterns = ['**/*.py',
                        '**/*.c',
                        '**/*.h',
                        '**/*.cpp',
                        '**/*.hpp']
        src = []
        for pattern in src_patterns:
            src.extend([p for p in code_repo_path.glob(pattern)
                        if 'third_party' not in p.parts])
        return src

    def fix_path_prefixes(self, prefix_fixes, paths):
        fixed_paths = []
        for p in paths:
            for prefix, prefix_replacement in prefix_fixes:
                p = p.replace(prefix, prefix_replacement)
            fixed_paths.append(p)
        return fixed_paths

    def group_files_by_type(self, files):
        file_groups = OrderedDict([(t, []) for t in self.file_types])
        file_groups['other_type'] = []
        for f in files:
            for type_key in self.file_types:
                if f.endswith(self.file_types[type_key]):
                    file_groups[type_key].append(f)
                    break
            else:
                file_groups['other_type'].append(f)
        return file_groups

    def group_files_by_category(self, files, categories):
        file_groups = OrderedDict([(c, []) for c in categories])
        file_groups['other_category'] = []
        for f in files:
            for category in categories:
                if f.startswith(categories[category]):
                    file_groups[category].append(f)
                    break
            else:
                file_groups['other_category'].append(f)
        return file_groups

    def map_categories(self, categories, files):
        groups = self.group_files_by_category(files, categories)
        return [len(group) for group in groups.values()]

    def assign_file_categories(self, ticket_frame: pd.DataFrame, categories):
        cat_columns = list(categories.keys()) + ['other_category']
        cat_data = ticket_frame.ChangedFiles.map(partial(self.map_categories,
                                                         categories))
        cat_frame = pd.DataFrame(data=cat_data.tolist(), columns=cat_columns)
        return pd.concat([ticket_frame, cat_frame], axis=1)

    def map_types(self, files):
        groups = self.group_files_by_type(files)
        return [len(group) for group in groups.values()]

    def assign_file_types(self, ticket_frame: pd.DataFrame) -> pd.DataFrame:
        type_columns = list(self.file_types.keys()) + ['other_type']
        type_data = ticket_frame.ChangedFiles.map(self.map_types)
        type_frame = pd.DataFrame(data=type_data.tolist(), columns=type_columns)
        frame: pd.DataFrame = pd.concat([ticket_frame, type_frame], axis=1)
        return frame

    def compute_commit_periods(self, ticket_frame: pd.DataFrame):
        commit_dates = ticket_frame.CommitDate
        commit_periods = self.compute_periods(commit_dates)
        commit_periods = pd.concat(
            [pd.Series(data=[pd.Timedelta(days=0)]),
             commit_periods]).reset_index(drop=True)
        ticket_frame.insert(8, 'CommitPeriod', commit_periods.dt.days)
        return ticket_frame

    def compute_periods(self, dates: pd.Series) -> pd.Series:
        high_dates = dates[1:]
        high_dates.reset_index(drop=True, inplace=True)
        low_dates = dates[:-1]
        low_dates.reset_index(drop=True, inplace=True)
        periods = high_dates - low_dates
        return periods

    def compute_periods_for_engineer(
            self, ticket_frame: pd.DataFrame, engineer: str):
        commit_dates = ticket_frame[
            ticket_frame.Engineer == engineer].CommitDate
        commit_periods = self.compute_periods(commit_dates)
        return commit_periods.dt.days

    def compute_mean_periods_by_engineer(self, ticket_frame: pd.DataFrame):
        engineers = ticket_frame.Engineer.unique()
        mean_periods = {
            engineer: self.compute_periods_for_engineer(
                ticket_frame, engineer).mean()
            for engineer in engineers}
        return pd.Series(data=mean_periods, name='MeanPeriod')

    def fix_tickets(
            self, ticket_frame: pd.DataFrame, path_fixes) -> pd.DataFrame:
        ticket_frame.rename(
            columns={'Total changed lines': 'ChangedLines'}, inplace=True)
        ticket_frame = ticket_frame[
            ticket_frame.ChangedLines < 100000]
        ticket_frame = ticket_frame.assign(
            ChangedFiles=ticket_frame['Changed files'].apply(
            partial(self.fix_path_prefixes, path_fixes)))
        fixed_frame = ticket_frame.drop(
            'Changed files', axis=1).sort_values(
            by='CommitDate').reset_index(drop=True)
        fixed_frame.fillna(value={'Found': ''}, axis=0, inplace=True)
        return fixed_frame

    # prj1 specific methods

    def load_prj1_project_metrics(self):
        return self.load_project_metrics(self.prj1_project_metrics_csv)

    def load_prj1_tickets(self) -> pd.DataFrame:
        return self.load_tickets(self.prj1_tickets_csv_path)

    prj1_path_fixes = (('//prod/main/prj1/', ''),
                      ('//prod/external_auth/', ''),
                      ('//prod/main/ap/', 'ap/'),
                      ('//prod/platform_reporting/', ''),
                      ('//prod/report_framework/ap/ui/report-framework/',
                       'prj1corecom/ui/webui/app/'),
                      ('//prod/tracking-1-9-1-br/', ''),
                      ('//prod/updater_client/', ''))

    def fix_prj1_tickets(self, ticket_frame: pd.DataFrame) -> pd.DataFrame:
        return self.fix_tickets(ticket_frame, self.prj1_path_fixes)

    prj1_file_categories = OrderedDict([
        ('prj1corecom_ui', 'prj1corecom/ui/'), ('ap', 'ap/'), ('build', 'env/'),
        ('os', 'freebsd/'), ('report', 'platform_reporting/'),
        ('prj1corecom_conf', 'prj1corecom/config/'), ('prj1corecom_godlib', 'prj1corecom/godlib/'),
        ('prj1corecom_subcore', 'prj1corecom/subcore/'), ('prj1corecom_openssl', 'prj1corecom/misc/openssl_'),
        ('prj1corecom_packages', 'prj1corecom/packages/'), ('prj1corecom_tests', 'prj1corecom/unittests/'),
        ('prj1corecom_other', 'prj1corecom/')])

    def assign_prj1_file_categories(self, ticket_frame: pd.DataFrame):
        return self.assign_file_categories(ticket_frame,
                                           self.prj1_file_categories)

    def prepare_prj1_tickets(self):
        prj1_tickets = self.load_prj1_tickets()
        prj1_tickets = self.fix_prj1_tickets(prj1_tickets)
        prj1_tickets = self.compute_commit_periods(prj1_tickets)
        prj1_tickets = self.assign_file_types(prj1_tickets)
        prj1_tickets = self.assign_prj1_file_categories(prj1_tickets)
        return prj1_tickets

    def collect_prj1_source_files(self):
        return self.collect_source_files(self.prj1_code_repo_path)

    def build_prj1_understand_project(self):
        if not self.prj1_scitools_client.project_exists():
            source_files = self.collect_prj1_source_files()
            self.prj1_scitools_client.create_project('python', 'c++')
            self.prj1_scitools_client.add_files_to_project(
                f for f in source_files)
            self.prj1_scitools_client.analyze_project()

    def build_prj1_code_graph(self):
        if not self.prj1_scitools_client.project_exists():
            print('understand project does not exist, '
                  'first run "$ prj1 understand --build"')
        else:
            with shelve.open(str(self.shelve_prj1_code_db_path)) as db:
                self.prj1_scitools_client.open_project()
                scitools_project = self.prj1_scitools_client.build_project(
                    self.prj1_code_repo_path)
                self.prj1_scitools_client.close_project()
                db['code_graph'] = scitools_project
                print('loaded scitools project of size',
                      len(scitools_project.code_graph))
                print('entity kinds:', scitools_project.entity_kinds)
                print('ref kinds:', scitools_project.ref_kinds)

    def load_prj1_metrics(self):
        return pd.read_csv(self.prj1_metrics_csv)

    # prj2 specific methods

    def load_prj2_project_metrics(self):
        return self.load_project_metrics(self.prj2_project_metrics_csv)

    def load_prj2_tickets(self) -> pd.DataFrame:
        return self.load_tickets(self.prj2_tickets_csv_path)

    prj2_path_fixes = (('//prod/main/prj2/', ''),)

    def fix_prj2_tickets(self, ticket_frame: pd.DataFrame) -> pd.DataFrame:
        ticket_frame = self.fix_tickets(ticket_frame, self.prj2_path_fixes)
        ticket_frame = ticket_frame[ticket_frame['ChangedFiles'].map(
            lambda files: any(not f.startswith('//prod') for f in files))]
        return ticket_frame

    prj2_file_categories = OrderedDict([
        ('prj2corecom_traffic_monitor', 'prj2corecom/traffic_monitor/'),
        ('prj2corecom_translate', 'prj2corecom/share/locale/'),
        ('prj2corecom_packages', 'prj2corecom/packages/'),
        ('prj2corecom_hybrid', 'prj2corecom/hybrid/'),
        ('prj2corecom_archivescan', 'prj2corecom/archivescan/'),
        ('prj2corecom_config', 'prj2corecom/config/'),
        ('prj2corecom_configdefragd', 'prj2corecom/configdefragd/'),
        ('prj2corecom_release', 'prj2corecom/release/'), ('prj2corecom_c3', 'prj2corecom/c3/'),
        ('prj2corecom_ui', 'prj2corecom/ui/'), ('prj2corecom_tests', 'prj2corecom/unittests/'),
        ('prj2corecom_other', 'prj2corecom/'), ('ci', 'CI_Automation/')])

    def assign_prj2_file_categories(self, ticket_frame: pd.DataFrame):
        return self.assign_file_categories(ticket_frame,
                                           self.prj2_file_categories)

    def prepare_prj2_tickets(self):
        tickets = self.load_prj2_tickets()
        tickets = self.fix_prj2_tickets(tickets)
        tickets = self.compute_commit_periods(tickets)
        tickets = self.assign_file_types(tickets)
        tickets = self.assign_prj2_file_categories(tickets)
        return tickets

    def load_prj2_metrics(self):
        return pd.read_csv(self.prj2_metrics_csv)

    def collect_prj2_source_files(self):
        return self.collect_source_files(self.prj2_code_repo_path)

    def build_prj2_understand_project(self):
        if not self.prj2_scitools_client.project_exists():
            source_files = self.collect_prj2_source_files()
            self.prj2_scitools_client.create_project('python', 'c++')
            self.prj2_scitools_client.add_files_to_project(
                f for f in source_files)
            self.prj2_scitools_client.analyze_project()


# noinspection PyMissingOrEmptyDocstring
class NotebookSupport:
    tickets: pd.DataFrame
    project: str

    def __init__(self, project='prj1'):
        if project not in ('prj1', 'prj2'):
            raise ValueError(
                'project type is {}, can be only prj1 or prj2'.format(project))
        self.project = project
        pd.options.display.float_format = '{:,.1f}'.format
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        warnings.filterwarnings('ignore', category=UserWarning)
        self.ws = Assessment(Path.cwd())
        sns.set_context("notebook", font_scale=1.5, rc={"lines.linewidth": 2.5})
        plt.rcParams['figure.figsize'] = (16, 6)
        self.color_map = sns.color_palette("Paired")
        if project == 'prj1':
            self.tickets = self.ws.prepare_prj1_tickets()
            self.metrics = self.ws.load_prj1_metrics()
            self.project_metrics = self.ws.load_prj1_project_metrics()
        else:
            self.tickets = self.ws.prepare_prj2_tickets()
            self.metrics = self.ws.load_prj2_metrics()
            self.project_metrics = self.ws.load_prj2_project_metrics()
        self.changed_lines = self.tickets.ChangedLines
        self.engineer_groups = self.tickets.groupby('Engineer')
        general_engineer_stats = [
            self.engineer_groups.CommitDate.min(),
            self.engineer_groups.CommitDate.max(),
            self.ws.compute_mean_periods_by_engineer(self.tickets),
            # self.engineer_groups['CommitPeriodDays'].mean(),
            self.engineer_groups.Identifier.count(),
            self.engineer_groups.ChangedLines.sum(),
            self.engineer_groups['python'].sum(),
            self.engineer_groups['template'].sum(),
            self.engineer_groups['c'].sum(),
            self.engineer_groups['patch'].sum(),
            self.engineer_groups['config'].sum(),
            self.engineer_groups['shell'].sum()]
        if project == 'prj1':
            all_engineer_stats = general_engineer_stats + [
                self.engineer_groups['prj1corecom_ui'].sum(),
                self.engineer_groups['os'].sum()]
        else:
            all_engineer_stats = general_engineer_stats + [
                self.engineer_groups['prj2corecom_ui'].sum()]
        self._engineer_stats = pd.concat(
            all_engineer_stats, axis=1).reset_index()
        changed_file_types = self.tickets[
            list(FILE_TYPES.keys()) + ['other_type']].sum()
        self.changed_file_type_frame = changed_file_types.rename(
            'Files').to_frame()
        if project == 'prj1':
            categories = self.ws.prj1_file_categories.keys()
        else:
            categories = self.ws.prj2_file_categories.keys()
        changed_file_categories = self.tickets[
            list(categories) + ['other_category']].sum()
        self.changed_file_category_frame = changed_file_categories.rename(
            'Files').to_frame()
        self.file_metrics = \
            self.metrics[self.metrics.Kind.str.endswith('File')][[
                'Name', 'CountLineCode', 'RatioCommentToCode', 'AvgEssential',
                'MaxEssential', 'SumEssential']]
        self.file_metrics = self.file_metrics.reset_index(drop=True)
        # noinspection PyTypeChecker
        self.changed_files = self.ws.collect_changed_files(self.tickets)
        self.changed_file_metrics = self.file_metrics[
            self.file_metrics.Name.isin(self.changed_files.keys())]
        self.tickets = pd.concat([self.tickets, pd.DataFrame(
            data=self.tickets.ChangedFiles.map(self.map_metrics).tolist(),
            columns=[
                'CountLineCode', 'RatioCommentToCode', 'AvgEssential',
                'MaxEssential', 'SumEssential'])], axis=1)

    def plot_palette(self):
        sns.palplot(self.color_map)

    def map_metrics(self, files):
        mf = self.changed_file_metrics[
            self.changed_file_metrics.Name.isin(files)]
        return [mf.CountLineCode.sum(),
                mf.RatioCommentToCode.mean(),
                mf.AvgEssential.mean(),
                mf.MaxEssential.max(),
                mf.SumEssential.sum()] if len(mf) else 5 * [0]

    def describe_tickets(self):
        return self.tickets.describe().T

    def describe_commit_periods(self):
        return self.tickets.CommitPeriod.describe()

    def histogram_commit_periods(self):
        plt.hist(self.tickets.CommitPeriod, bins=20,
                 color=self.color_map[1])

    def plot_commit_periods(self):
        plt.plot(self.tickets.CommitDate, self.tickets.CommitPeriod,
                 'ro', color=self.color_map[1])

    def describe_changed_lines(self):
        return self.changed_lines.describe()

    def histogram_changed_lines(self):
        plt.hist(self.changed_lines, bins=30, color=self.color_map[3])

    def plot_changed_lines(self, outlayers=200):
        plt.plot(self.tickets.CommitDate,
                 self.changed_lines.where(self.changed_lines < outlayers), 'ro',
                 color=self.color_map[3])

    def print_unique_committer_count(self):
        committers = self.tickets.Engineer.unique()
        print('Number of unique committers:', len(committers))

    def plot_commits_by_engineer(self):
        plt.figure(figsize=(16, 14))
        sns.stripplot(x="CommitDate", y="Engineer", data=self.tickets,
                      jitter=True)

    def engineer_stats(self):
        return self._engineer_stats

    def plot_changed_files_by_type(self):
        sns.barplot(x="Files", y=self.changed_file_type_frame.index,
                    data=self.changed_file_type_frame)

    def plot_changed_files_by_category(self):
        sns.barplot(x="Files", y=self.changed_file_category_frame.index,
                    data=self.changed_file_category_frame)

    def describe_file_metrics(self):
        return self.file_metrics.describe()

    def describe_changed_file_metrics(self):
        return self.changed_file_metrics.describe()

    def most_complex_changed_files(self):
        return self.changed_file_metrics[
            self.changed_file_metrics.MaxEssential > 20]

    def describe_ticket_metrics(self):
        return self.ticket_metrics[
            self.ticket_metrics.CountLineCode > 0].describe().T

    def describe_commit_periods_for_complex_files(self):
        return self.tickets[
            self.tickets.SumEssential > 90].CommitPeriod.describe()


if __name__ == '__main__':
    ws = Assessment(Path.cwd())
    # prj1_tickets = ws.prepare_prj1_tickets()
    # print(ws.collect_changed_files(prj1_tickets))
    metrics_frame = ws.load_prj1_metrics()
    file_metrics = metrics_frame[metrics_frame.Kind == 'File']
    print(file_metrics[['CountLineCode', 'SumEssential',
                        'RatioCommentToCode']].describe())
