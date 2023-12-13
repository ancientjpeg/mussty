from collections.abc import Callable, Iterable, Mapping
import threading
from typing import Any, Callable


class ThreadpoolManager:
    class Thread(threading.Thread):
        def __init__(
            self,
            group: None = None,
            target: Callable[..., object] | None = None,
            name: str | None = None,
            args: Iterable[Any] = ...,
            kwargs: Mapping[str, Any] | None = None,
            *,
            daemon: bool | None = None
        ) -> None:
            super().__init__(group, target, name, args, kwargs, daemon=daemon)

    class Job:
        job: Callable
        args: list
        kwargs: dict

        def __init__(self, job: Callable, *args, **kwargs) -> None:
            self.job = job
            self.args = args
            self.kwargs = kwargs

        def run(self):
            self.job(*self.args, **self.kwargs)

    instance = None

    def __init__(self) -> None:
        self.jobs: list = []

    def __new__(cls):
        if cls.instance == None:
            cls.instance = ThreadpoolManager()
        return cls.instance

    def run_job(self, job: Callable, *args, **kwargs):
        pool_job = ThreadpoolManager.Job(job, *args, **kwargs)
        self.jobs.append(pool_job)
