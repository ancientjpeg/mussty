import threading
from requests import Session
from typing import Callable


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


class ThreadpoolManager:
    session: Session

    def __init__(self) -> None:
        self.session = Session()

    def run_job(job: Callable, *args, **kwargs):
        pool_job = Job(job, *args, **kwargs)
