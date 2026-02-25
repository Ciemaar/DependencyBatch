import os
import shutil
import tarfile
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any


class Job(ABC):  # noqa: B024
    def __init__(self) -> None:
        self.depends_on: list[Job] = []
        self.result_of: list[Job] = []
        self.results: list[Any] = []
        self.local_dir: str | None = None

    def close(self) -> None:
        """Cleanup any local files and close the job."""
        if self.local_dir and os.path.isdir(self.local_dir):
            shutil.rmtree(self.local_dir)
        self.local_dir = None

    def get_local_folder(self) -> str:
        """Get a local folder with the files of this job.

        The base class implementation of this method assumes that get_tar() is
        implemented and can be used to get the data.
        """
        if self.local_dir:
            return self.local_dir
        self.local_dir = tempfile.mkdtemp()
        tar = self.get_tar()
        tar.extractall(self.local_dir, filter="data")
        tar.close()
        return self.local_dir

    def get_filenames(self) -> list[str]:
        """Get the local filenames for this Job retrieving if necessary.

        The base class assumes that get_local_folder() is implemented and can be used
        to get the folder to check.
        """
        # TODO: Make this recursive
        folder = self.get_local_folder()
        return [os.path.join(folder, f) for f in os.listdir(folder)]

    def get_tar(self, compression: str = "gz") -> tarfile.TarFile:
        """Get the data related to this job as a tar file object.

        The base class assumes that get_filenames() is implemented and can be used
        to get the files to pack.

        compression:
           ''         no compression/automatic compression
           'gz'       gzip compression
           'bz2'      bzip2 compression
           'xz'       lzma compression
        """
        mode = "w:" + compression
        fileobj = tempfile.TemporaryFile()  # noqa: SIM115

        # Open tar for writing
        with tarfile.open(fileobj=fileobj, mode=mode) as tfile:  # type: ignore[call-overload]
            for file_path in self.get_filenames():
                tfile.add(
                    file_path, arcname=os.path.basename(file_path), recursive=True
                )

        # Seek to beginning to allow reading
        fileobj.seek(0)

        # Return a TarFile object opened for reading
        return tarfile.open(fileobj=fileobj, mode="r:*")  # type: ignore[call-overload]


class QueuedJob(Job):
    """A default implementation of Job."""

    pass


class Queue(ABC):
    def __init__(self, job_class: type[Job] = QueuedJob) -> None:
        self.openJobs: dict = {}
        self.job_class = job_class

    @abstractmethod
    def queue_job(self, job: Job) -> None:
        """
        Add the given job to this queue
        """
        pass

    def jobs(self) -> Iterator[Job]:
        """
        A generator that returns jobs
        the same job will not be returned twice by the
        same queue object
        """
        return iter(self.allJobs())

    @abstractmethod
    def allJobs(self) -> list[Job]:
        pass

    @abstractmethod
    def delete(self, job: Job) -> None:
        pass


class LocalQueue(Queue):
    """A concrete Queue implementation using a local list."""

    def __init__(self, job_class: type[Job] = QueuedJob) -> None:
        super().__init__(job_class)
        self._jobs: list[Job] = []

    def queue_job(self, job: Job) -> None:
        self._jobs.append(job)

    def allJobs(self) -> list[Job]:
        return list(self._jobs)

    def delete(self, job: Job) -> None:
        if job in self._jobs:
            self._jobs.remove(job)
