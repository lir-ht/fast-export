import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase
from pathlib import Path


class CommitDropTest(TestCase):
    def setUp(self):
        self.tempdir = TemporaryDirectory()
        self.hg = HgDriver(self.tempdir.name)

    def tearDown(self):
        self.tempdir.cleanup()

    def run_hg(self, *args):
        return self.hg.run_command(*args)

    def write_file_data(self, data, filename='test_file.txt'):
        path = Path(self.tempdir.name) / filename
        with path.open('w') as f:
            print(data, file=f)

    def test_drop_single_commit(self):
        self.write_file_data('line 1')
        self.hg.init()
        self.hg.commit('commit 1')

        self.assertEqual('0 commit 1', self.hg.log())


class HgDriver:
    def __init__(self, repodir):
        self.repodir = Path(repodir)

    def run_command(self, *args):
        p = subprocess.run(('hg', '-yq') + args,
                           cwd=str(self.repodir),
                           check=True,
                           text=True,
                           capture_output=True)
        return p.stdout

    def init(self):
        self.run_command('init')

    def commit(self, message):
        self.run_command('commit', '-A', '-m', message)

    def log(self):
        return self.run_command('log', '-T', '{rev} {desc}')
