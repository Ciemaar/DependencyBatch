"""
This module provides abstract base classes and default implementations for managing
jobs and queues. It includes support for local file handling and tarball archiving.
"""

import os
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
        self.depends_on: set[Job] = set()
        self.result_of: set[Job] = set()
        self.results: set[Path] = set()
        self.local_dir: Path | None = None

    def __enter__(self) -> Path:
        return self.get_local_folder()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: Any | None,
    ) -> None:
        self.close()

    def close(self) -> None:
        """Cleanup any local files and close the job."""
        self.handle_results()
        if self.local_dir and self.local_dir.is_dir():
            shutil.rmtree(self.local_dir)
        self.local_dir = None

    def handle_results(self) -> None:
        """
        Compress the files in `self.results` into a temporary tar file
        and call `store_results` with the path to that tar file.
        """
        if not self.results:
            return

        # Create a temporary file to store the tar archive.
        # It's created outside of local_dir to ensure it survives
        # local_dir cleanup if store_results is asynchronous or delayed
        # (though store_results should ideally handle it synchronously).
        fd, temp_path_str = tempfile.mkstemp(suffix=".tar.gz")
        os.close(fd)
        temp_path = Path(temp_path_str)

        try:
            with tarfile.open(temp_path, mode="w:gz") as tar:
                for res_path in self.results:
                    if res_path.exists():
                        tar.add(res_path, arcname=res_path.name)

            self.store_results(temp_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    @abstractmethod
    def store_results(self, archive_path: Path) -> None:
        """
        Store the compressed results archive.

        Args:
            archive_path (Path): The path to the temporary tarball containing the
                                 results.
        """
        pass

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

    def store_results(self, archive_path: Path) -> None:
        """
        Default implementation for QueuedJob does nothing with the results.
        Subclasses should override this to upload or copy the archive.
        """
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
