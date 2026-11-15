"""Periodic graceful LPJmL checkpoints on Linux; preserve saved generations by default.

Use a dedicated phase directory and a config with an absolute checkpoint_filename.
SIGTERM goes only to rank zero belonging to this launch, never to mpirun.
An exit code of zero alone does not mean the scientific phase has completed.
An explicit archive limit can prune older copies only after a new generation is
copied and hashed; the active restart file remains separate from the archive.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import time


def rank_zero(parent):
    """Find rank zero by both OpenMPI rank and this launch's process ancestry."""
    for entry in Path('/proc').iterdir():
        if not entry.name.isdigit():
            continue
        try:
            env = (entry / 'environ').read_bytes().split(b'\0')
            if b'OMPI_COMM_WORLD_RANK=0' not in env:
                continue
            pid = int(entry.name)
            ancestor = pid
            while ancestor > 1:
                status = Path(f'/proc/{ancestor}/status').read_text()
                ancestor = int(re.search(r'^PPid:\s+(\d+)', status, re.M)[1])
                if ancestor == parent:
                    return pid
        except (OSError, ValueError, TypeError):
            continue
    return None


def prune_checkpoint_archives(archive, max_archived_checkpoints):
    """Keep the newest archived generations; zero preserves every generation."""
    if max_archived_checkpoints < 0:
        raise ValueError('max_archived_checkpoints must be non-negative')
    if max_archived_checkpoints == 0:
        return []

    generations = sorted(
        Path(archive).glob('*.lpj'),
        key=lambda path: path.stat().st_mtime_ns,
        reverse=True,
    )
    removed = generations[max_archived_checkpoints:]
    for checkpoint in removed:
        checkpoint.unlink()
        sidecar = checkpoint.with_suffix('.sha256')
        if sidecar.exists():
            sidecar.unlink()
    return removed


def sha256_file(path):
    """Hash a checkpoint in bounded memory."""
    hasher = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(block)
    return hasher.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--phase-dir', type=Path, required=True)
    parser.add_argument('--interval-seconds', type=float, default=3600)
    parser.add_argument('--not-before-year', type=int)
    parser.add_argument('--max-checkpoints', type=int, default=0,
                        help='Stop after this many saves; zero continues to completion.')
    parser.add_argument('--max-archived-checkpoints', type=int, default=0,
                        help=('Retain only the newest archived generations after a '
                              'new checkpoint has been copied and hashed; zero keeps all.'))
    parser.add_argument('command', nargs=argparse.REMAINDER)
    args = parser.parse_args()
    command = args.command[1:] if args.command[:1] == ['--'] else args.command
    config = json.loads(args.config.read_text())
    checkpoint = Path(config['checkpoint_filename'])
    if (not checkpoint.is_absolute() or not command or args.interval_seconds <= 0 or
            args.max_archived_checkpoints < 0):
        parser.error('Require absolute checkpoint path, positive interval, non-negative '
                     'archive limit and command.')
    args.phase_dir.mkdir(parents=True, exist_ok=True)
    import fcntl
    lock = (args.phase_dir / 'checkpoint_runner.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    archive = args.phase_dir / 'checkpoints'
    archive.mkdir(exist_ok=True)
    saves = 0
    while True:
        tag = str(time.time_ns())
        log = args.phase_dir / f'segment_{tag}.stdout.log'
        previous = checkpoint.stat().st_mtime_ns if checkpoint.exists() else None
        with log.open('w') as stdout, log.with_suffix('.stderr.log').open('w') as stderr:
            proc = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            start = time.monotonic()
            sent = False
            while proc.poll() is None:
                # Wait for annual output: the solver installs its handler in iterate().
                years = re.findall(r'^\s*(-?\d+)\s+[-\d.]+\s', log.read_text(), re.M)
                ready = years and (args.not_before_year is None or
                                   int(years[-1]) >= args.not_before_year)
                if not sent and ready and time.monotonic() - start >= args.interval_seconds:
                    pid = rank_zero(proc.pid)
                    if pid is not None:
                        os.kill(pid, signal.SIGTERM)
                        sent = True
                time.sleep(0.25)
        if proc.returncode:
            raise RuntimeError(f'LPJmL exit {proc.returncode}; inspect {log}')
        content = log.read_text()
        if 'checkpoint file' in content and 'SIGTERM catched' in content:
            if not checkpoint.exists() or checkpoint.stat().st_size == 0:
                raise RuntimeError('Reported checkpoint missing or empty')
            if checkpoint.stat().st_mtime_ns == previous:
                raise RuntimeError('Checkpoint did not change')
            saved = archive / f'{tag}.lpj'
            shutil.copy2(checkpoint, saved)
            digest = sha256_file(saved)
            if digest != sha256_file(checkpoint):
                saved.unlink()
                raise RuntimeError('Archived checkpoint hash does not match active restart')
            saved.with_suffix('.sha256').write_text(digest + '\n')
            print(f'CHECKPOINT_SAVED {saved} sha256={digest}', flush=True)
            for removed in prune_checkpoint_archives(
                    archive, args.max_archived_checkpoints):
                print(f'CHECKPOINT_PRUNED {removed}', flush=True)
            saves += 1
            if args.max_checkpoints and saves >= args.max_checkpoints:
                return
        else:
            if checkpoint.exists():
                raise RuntimeError('Exit without checkpoint message but checkpoint remains')
            print('PHASE_EXIT_ZERO_PENDING_SCIENTIFIC_VALIDATION', flush=True)
            return


if __name__ == '__main__':
    main()
