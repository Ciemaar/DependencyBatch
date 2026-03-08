"""
This module provides abstract base classes and default implementations for managing
jobs and queues. It includes support for local file handling and tarball archiving.
"""

import shutil
import tarfile
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Iterator
from pathlib import Path
from typing import Any


class Job(ABC):  # noqa: B024
    """
    Abstract base class representing a job.

    A job can have dependencies, results, and associated local files.
    """

    def __init__(self) -> None:
        self.depends_on: list[Job] = []
        self.result_of: list[Job] = []
        self.results: list[Any] = []
        self.local_dir: Path | None = None

    def close(self) -> None:
        """Cleanup any local files and close the job."""
        if self.local_dir and self.local_dir.is_dir():
            shutil.rmtree(self.local_dir)
        self.local_dir = None

    def get_local_folder(self) -> Path:
        """Get a local folder with the files of this job.

        The base class implementation of this method assumes that get_tar() is
        implemented and can be used to get the data.

        Returns:
            Path: The path to the local directory containing the job's files.
        """
        if self.local_dir:
            return self.local_dir
        self.local_dir = Path(tempfile.mkdtemp())
        tar = self.get_tar()
        tar.extractall(self.local_dir, filter="data")
        tar.close()
        return self.local_dir

    def get_filenames(self) -> list[Path]:
        """Get the local filenames for this Job retrieving if necessary.

        The base class assumes that get_local_folder() is implemented and can be used
        to get the folder to check.

        Returns:
            list[Path]: A list of file paths.
        """
        # TODO: Make this recursive
        folder = self.get_local_folder()
        return [f for f in folder.iterdir() if f.is_file()]

    def get_tar(self, compression: str = "gz") -> tarfile.TarFile:
        """Get the data related to this job as a tar file object.

        The base class assumes that get_filenames() is implemented and can be used
        to get the files to pack.

        Args:
            compression (str): Compression mode.
                ''         no compression/automatic compression
                'gz'       gzip compression
                'bz2'      bzip2 compression
                'xz'       lzma compression

        Returns:
            tarfile.TarFile: A TarFile object opened for reading.
        """
        mode = "w:" + compression
        fileobj = tempfile.TemporaryFile()  # noqa: SIM115

        # Open tar for writing
        with tarfile.open(fileobj=fileobj, mode=mode) as tfile:  # type: ignore[call-overload]
            for file_path in self.get_filenames():
                tfile.add(file_path, arcname=file_path.name, recursive=True)

        # Seek to beginning to allow reading
        fileobj.seek(0)

        # Return a TarFile object opened for reading
        return tarfile.open(fileobj=fileobj, mode="r:*")


class QueuedJob(Job):
    """A default implementation of Job."""

    pass


class Queue(ABC):
    """
    Abstract base class representing a job queue.
    """

    def __init__(self, job_class: type[Job] = QueuedJob) -> None:
        self.openJobs: dict = {}
        self.job_class = job_class

    @abstractmethod
    def queue_job(self, job: Job) -> None:
        """
        Add the given job to this queue.

        Args:
            job (Job): The job to add to the queue.
        """
        pass

    def jobs(self) -> Iterator[Job]:
        """
        A generator that returns jobs.

        The same job will not be returned twice by the same queue object.

        Yields:
            Job: The next job in the queue.
        """
        return iter(self.allJobs())

    @abstractmethod
    def allJobs(self) -> list[Job]:
        """
        Get all jobs currently in the queue.

        Returns:
            list[Job]: A list of all jobs.
        """
        pass

    @abstractmethod
    def delete(self, job: Job) -> None:
        """
        Remove a job from the queue.

        Args:
            job (Job): The job to remove.
        """
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
