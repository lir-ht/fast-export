import subprocess
from tempfile import TemporaryDirectory
from unittest import TestCase
from pathlib import Path


class CommitDropTest(TestCase):
    def setUp(self):
        self.tempdir = TemporaryDirectory()

    def tearDown(self):
        self.tempdir.cleanup()

    def run_hg(self, *args):
        p = subprocess.run(("hg", "-yq") + args,
                           cwd=self.tempdir.name,
                           check=True,
                           text=True,
                           capture_output=True)
        return p.stdout

    def write_file(self, name, data):
        path = Path(self.tempdir.name) / name
        with path.open('w') as f:
            print(data, file=f)

    def test_drop_single_commit(self):
        self.run_hg("init")
        self.write_file("test_file.txt", "line 1")
        self.run_hg("commit", "-A", "-m", "commit 1")

        log = self.run_hg("log", "-T", "{rev} {desc}")
        self.assertEqual("0 commit 1", log)

