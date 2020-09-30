import sys, subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase
from pathlib import Path


class CommitDropTest(TestCase):
    def test_drop_single_commit(self):
        commit1_hash = self.create_commit('commit 1')
        self.create_commit('commit 2')

        self.export.run_with_drop(commit1_hash)

        self.assertEqual(['commit 2'], self.git.log())

    def setUp(self):
        self.tempdir = TemporaryDirectory()

        self.hg = HgDriver(Path(self.tempdir.name) / 'hgrepo')
        self.hg.init()

        self.git = GitDriver(Path(self.tempdir.name) / 'gitrepo')
        self.git.init()

        self.export = ExportDriver(self.hg.repodir, self.git.repodir)

    def tearDown(self):
        self.tempdir.cleanup()

    def create_commit(self, message):
        self.write_file_data('Data for %r.' % message)
        return self.hg.commit(message)

    def write_file_data(self, data, filename='test_file.txt'):
        path = self.hg.repodir / filename
        with path.open('w') as f:
            print(data, file=f)


class ExportDriver:
    def __init__(self, sourcedir, targetdir, *, quiet=True):
        self.sourcedir = Path(sourcedir)
        self.targetdir = Path(targetdir)
        self.quiet = quiet
        self.python_executable = sys.executable
        self.script = Path(__file__).parent / '../hg-fast-export.sh'

    def run_with_drop(self, *plugin_args):
        cmd = [self.script, '-r', str(self.sourcedir)]
        for arg in plugin_args:
            cmd.extend(['--plugin', 'drop=' + arg])
        output = subprocess.DEVNULL if self.quiet else None
        subprocess.run(cmd, check=True, cwd=str(self.targetdir),
                       env={'PYTHON': self.python_executable},
                       stdout=output, stderr=output)


class HgDriver:
    def __init__(self, repodir):
        self.repodir = Path(repodir)

    def init(self):
        self.repodir.mkdir()
        self.run_command('init')

    def commit(self, message):
        self.run_command('commit', '-A', '-m', message)
        return self.run_command('id', '--id', '--debug').strip()

    def log(self):
        output = self.run_command('log', '-T', '{desc}\n')
        commits = output.strip().split('\n')
        commits.reverse()
        return commits

    def run_command(self, *args):
        p = subprocess.run(('hg', '-yq') + args,
                           cwd=str(self.repodir),
                           check=True,
                           text=True,
                           capture_output=True)
        return p.stdout


class GitDriver:
    def __init__(self, repodir):
        self.repodir = Path(repodir)

    def init(self):
        self.repodir.mkdir()
        self.run_command('init')

    def log(self):
        output = self.run_command('log', '--format=%s', '--reverse')
        return output.strip().split('\n')

    def run_command(self, *args):
        p = subprocess.run(('git', '--no-pager') + args,
                           cwd=str(self.repodir),
                           check=True,
                           text=True,
                           capture_output=True)
        return p.stdout
