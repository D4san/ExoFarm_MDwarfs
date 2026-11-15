import os
import tempfile
import unittest
from pathlib import Path

from checkpoint_runner import prune_checkpoint_archives


class CheckpointRetentionTests(unittest.TestCase):
    def make_generations(self, archive, count):
        paths = []
        for index in range(count):
            checkpoint = archive / f"generation_{index}.lpj"
            checkpoint.write_bytes(f"checkpoint {index}".encode())
            checkpoint.with_suffix(".sha256").write_text(f"hash {index}\n")
            os.utime(checkpoint, ns=(index + 1, index + 1))
            paths.append(checkpoint)
        return paths

    def test_zero_keeps_all_generations(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory)
            paths = self.make_generations(archive, 4)

            removed = prune_checkpoint_archives(archive, 0)

            self.assertEqual(removed, [])
            self.assertTrue(all(path.exists() for path in paths))
            self.assertTrue(all(path.with_suffix(".sha256").exists() for path in paths))

    def test_limit_keeps_newest_generations_and_removes_sidecars(self):
        with tempfile.TemporaryDirectory() as directory:
            archive = Path(directory)
            paths = self.make_generations(archive, 5)

            removed = prune_checkpoint_archives(archive, 2)

            self.assertEqual(set(removed), set(paths[:3]))
            self.assertEqual(set(archive.glob("*.lpj")), set(paths[3:]))
            self.assertTrue(all(path.with_suffix(".sha256").exists() for path in paths[3:]))
            self.assertTrue(all(not path.with_suffix(".sha256").exists() for path in paths[:3]))


if __name__ == "__main__":
    unittest.main()
