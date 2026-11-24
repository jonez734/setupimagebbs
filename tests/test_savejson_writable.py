"""savejson's writability check: an existing file must be writable; a new file needs a writable directory.

The old check called os.access(filename, W_OK | F_OK) on the target path. For a file that does not exist yet that is
False, so a fresh save was refused as "not writable".
"""

import os
import tempfile
import unittest

from setupimagebbs import savejson


class TestWritableTarget(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.addCleanup(lambda: os.path.isdir(self.dir) and __import__("shutil").rmtree(self.dir, ignore_errors=True))

    def test_a_new_file_in_a_writable_directory_is_writable(self):
        self.assertTrue(savejson.target_writable(os.path.join(self.dir, "gfd3.json")))

    def test_an_existing_writable_file_is_writable(self):
        path = os.path.join(self.dir, "gfd3.json")
        open(path, "w").close()
        self.assertTrue(savejson.target_writable(path))

    def test_an_existing_read_only_file_is_not_writable(self):
        path = os.path.join(self.dir, "gfd3.json")
        open(path, "w").close()
        os.chmod(path, 0o444)
        self.addCleanup(os.chmod, path, 0o644)
        if os.access(path, os.W_OK):  # running as root: permissions do not restrict
            self.skipTest("permission bits do not apply to this user")
        self.assertFalse(savejson.target_writable(path))

    def test_a_new_file_in_a_missing_directory_is_not_writable(self):
        self.assertFalse(savejson.target_writable(os.path.join(self.dir, "nope", "gfd3.json")))


if __name__ == "__main__":
    unittest.main()
