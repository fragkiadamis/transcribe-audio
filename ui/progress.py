import tqdm as tqdm_module
from contextlib import contextmanager

import whisper
from rich.progress import BarColumn, Progress, SpinnerColumn, TaskProgressColumn, TextColumn, TimeElapsedColumn


def _make_tqdm_class(on_progress):
    """Returns a tqdm-compatible class that routes updates to an on_progress callback."""
    class _T:
        def __init__(self, *args, total=None, **kwargs):
            if total is not None:
                on_progress(advance=0, total=total)

        def __enter__(self):
            return self

        def __exit__(self, *args):
            pass

        def update(self, n=1):
            on_progress(advance=n)

        def close(self):
            pass

        def set_postfix(self, **kwargs):
            pass

    return _T


class ProgressManager:
    def __init__(self):
        self._progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        )

    def __enter__(self):
        self._progress.__enter__()
        return self

    def __exit__(self, *args):
        self._progress.__exit__(*args)

    def _make_callback(self, task_id):
        def callback(advance=1, total=None):
            if total is not None:
                self._progress.update(task_id, total=total)
            if advance:
                self._progress.advance(task_id, advance)
        return callback

    def _complete(self, task_id, description):
        task = next(t for t in self._progress.tasks if t.id == task_id)
        total = task.total if task.total is not None else 1
        self._progress.update(task_id, completed=total, total=total, description=description)

    @contextmanager
    def loading(self):
        task_id = self._progress.add_task("Loading model...", total=None)
        cb = self._make_callback(task_id)
        _orig = whisper.tqdm
        whisper.tqdm = _make_tqdm_class(cb)
        try:
            yield
        finally:
            whisper.tqdm = _orig
            self._complete(task_id, "Model loaded")

    @contextmanager
    def transcribing(self):
        task_id = self._progress.add_task("Transcribing...", total=None)
        cb = self._make_callback(task_id)
        _orig = tqdm_module.tqdm
        tqdm_module.tqdm = _make_tqdm_class(cb)
        try:
            yield
        finally:
            tqdm_module.tqdm = _orig
            self._complete(task_id, "Transcription done")

    @contextmanager
    def translating(self, total):
        task_id = self._progress.add_task("Translating...", total=total)
        yield self._make_callback(task_id)
        self._progress.update(task_id, description="Translation done")

    @contextmanager
    def saving(self, total):
        task_id = self._progress.add_task("Saving output...", total=total)
        yield self._make_callback(task_id)
        self._progress.update(task_id, description="Output saved")
