#!/usr/bin/env python3
"""Review store: atomic state and history updates with locking and recovery.

Shared storage primitives for Phase 7E and Phase 7G review writers.
"""

from __future__ import annotations

import contextlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Iterator


class ReviewStoreError(RuntimeError):
    """Base exception for review store operations."""


class ReviewLockError(ReviewStoreError):
    """Raised when the review lock is held by another writer."""


class HistoryAppendError(ReviewStoreError):
    """Raised when history append fails and state is rolled back."""


class SnapshotExistsError(ReviewStoreError, FileExistsError):
    """Raised when snapshot already exists to refuse overwrite."""


@contextlib.contextmanager
def review_lock(audit_dir: Path) -> Iterator[Path]:
    """Acquire an exclusive lock file in audit_dir without blocking.

    Creates audit_dir / ".review.lock" with O_CREAT | O_EXCL | O_WRONLY and
    writes the current process PID into it. If the lock already exists, raises
    ReviewLockError naming the holding lock file. Removes the lock in finally.
    """
    audit_dir = Path(audit_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    lock_path = audit_dir / ".review.lock"

    acquired = False
    try:
        try:
            fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except (FileExistsError, OSError) as exc:
            if lock_path.exists():
                raise ReviewLockError(
                    f"review lock held by another writer ({lock_path}); "
                    f"if stale, remove {lock_path}"
                ) from exc
            raise
        acquired = True
        try:
            os.write(fd, f"{os.getpid()}\n".encode("utf-8"))
        finally:
            os.close(fd)
        yield lock_path
    finally:
        if acquired:
            try:
                lock_path.unlink()
            except OSError:
                pass


def _atomic_copy_replace(src_path: Path, dest_path: Path) -> None:
    """Atomically copy src_path over dest_path using a temp file in dest_path.parent."""
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=dest_path.parent,
            prefix=f".{dest_path.name}.restore.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_path = Path(tmp.name)
            with open(src_path, "rb") as src:
                shutil.copyfileobj(src, tmp)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, dest_path)
        tmp_path = None
    finally:
        if tmp_path is not None and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass


def commit_state_and_history(
    state_path: Path,
    new_state: dict,
    history_path: Path,
    events: list[dict],
    snapshot_path: Path,
) -> None:
    """Commit state and history as one recoverable operation.

    1. Snapshot before state write: refuse to overwrite existing snapshot.
    2. Atomic state write: write JSON formatted as `indent=2, ensure_ascii=False`
       plus trailing newline to a temp file, flush and fsync, then atomic replace.
    3. History append with recovery: record pre-append size, append all events
       in a single write call, flush and fsync. If append raises, truncate history
       back to recorded size and restore state_path from snapshot_path via atomic replace.
    """
    state_path = Path(state_path)
    history_path = Path(history_path)
    snapshot_path = Path(snapshot_path)

    # 1. Snapshot: refuse to overwrite an existing snapshot.
    if snapshot_path.exists():
        raise SnapshotExistsError(
            f"snapshot {snapshot_path.name} already exists; refusing to overwrite"
        )
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    if state_path.exists():
        shutil.copy(state_path, snapshot_path)

    # 2. Atomic state write
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_content = json.dumps(new_state, indent=2, ensure_ascii=False) + "\n"
    state_bytes = state_content.encode("utf-8")

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(
            dir=state_path.parent,
            prefix=f".{state_path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp.write(state_bytes)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_path, state_path)
        tmp_path = None
    finally:
        if tmp_path is not None and tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass

    # 3. History append with recovery
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_pre_exists = history_path.exists()
    history_pre_size = history_path.stat().st_size if history_pre_exists else 0

    history_payload = "".join(
        json.dumps(event, ensure_ascii=False) + "\n" for event in events
    ).encode("utf-8")

    try:
        with open(history_path, "ab") as fh:
            fh.write(history_payload)
            fh.flush()
            os.fsync(fh.fileno())
    except Exception as append_exc:
        # Rollback history append
        try:
            if history_pre_exists:
                with open(history_path, "r+b") as fh:
                    fh.truncate(history_pre_size)
                    fh.flush()
                    os.fsync(fh.fileno())
            else:
                if history_path.exists():
                    history_path.unlink()
        except Exception:
            pass

        # Rollback state write by restoring from snapshot
        try:
            if snapshot_path.exists():
                _atomic_copy_replace(snapshot_path, state_path)
        except Exception:
            pass

        raise HistoryAppendError(
            f"History append failed: {append_exc}; rolled back state from "
            f"{snapshot_path.name} and truncated history to {history_pre_size} bytes"
        ) from append_exc
