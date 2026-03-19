"""This module provides abstract base classes and default implementations for managing.

It includes support for local file handling and tarball archiving for jobs and queues.
"""

import os
import tarfile
import tempfile
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from pathlib import Path
from types import TracebackType


class Job(ABC):  # noqa: B024
    """Abstract base class representing a single unit of work in a queue.

    A `Job` encapsulates the logic for managing its dependencies, output results,
    and temporary local file processing. It is designed to act as a context manager,
    safely handling local directory creation and automated cleanup upon exit.
    """

    def __init__(self) -> None:
        """Initialize a new Job instance with empty dependencies and results.

        Sets up the basic tracking structures for dependency graphs (`depends_on`,
        `result_of`) and a set for tracking generated output files (`results`).
        """
        self.depends_on: set[Job] = set()
        self.result_of: set[Job] = set()
        self.results: set[Path] = set()
        self.local_dir: Path | None = None
        self._temp_dir_obj: tempfile.TemporaryDirectory[str] | None = None

    def __enter__(self) -> Path:
        """Enter the context manager, automatically providing a temporary workspace.

        This calls `get_local_folder()` to either extract an existing archive or
        create a fresh, isolated temporary directory for the job to operate within.

        Returns:
            Path: The absolute path to the job's temporary workspace.
        """
        return self.get_local_folder()

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Exit the context manager and trigger automatic cleanup.

        Ensures that `close()` is called regardless of whether the context exited
        cleanly or due to an exception. This guarantees that output results are
        processed and temporary directories are safely removed.

        Args:
            exc_type: The type of the exception that caused the context to exit.
            exc_val: The instance of the exception that caused the context to exit.
            exc_tb: The traceback corresponding to the exception.
        """
        self.close()

    def close(self) -> None:
        """Finalize the job lifecycle, process results, and perform cleanup.

        This method triggers `handle_results()` to compress and store any tracked
        output files. Afterward, it forcefully removes the temporary local workspace
        associated with this job to prevent disk space leaks.
        """
        self.handle_results()
        if self._temp_dir_obj:
            self._temp_dir_obj.cleanup()
            self._temp_dir_obj = None
        self.local_dir = None

    def handle_results(self) -> None:
        """Package and route tracked job outputs for long-term storage.

        If any file paths were added to the `self.results` set during execution,
        this method aggregates them into a highly-compressed, temporary `.tar.gz`
        archive. It then delegates the actual storage logic (like a cloud upload)
        to the abstract `store_results` method.
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
                    if not res_path.exists():
                        continue
                    tar.add(res_path, arcname=res_path.name)

            self.store_results(temp_path)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    @abstractmethod
    def store_results(self, archive_path: Path) -> None:
        """Define the custom storage destination for the job's final output archive.

        Subclasses must implement this method to dictate how the generated
        `.tar.gz` artifact is persisted (e.g., pushed to AWS S3, a database,
        or moved to a permanent local directory).

        Args:
            archive_path (Path): The path to the locally generated `.tar.gz`
                                 file containing the job's results.
        """
        pass  # pragma: no cover

    def get_local_folder(self) -> Path:
        """Establish or retrieve the local workspace directory for the job.

        If a workspace doesn't exist, it safely creates a temporary directory
        and populates it by extracting the job's underlying tarball data
        (via `get_tar()`), using strict security filters to prevent path traversal.

        Returns:
            Path: The path to the newly populated local workspace directory.
        """
        if self.local_dir:
            return self.local_dir
        self._temp_dir_obj = tempfile.TemporaryDirectory()
        self.local_dir = Path(self._temp_dir_obj.name)
        tar = self.get_tar()
        tar.extractall(self.local_dir, filter="data")
        tar.close()
        return self.local_dir

    def get_filenames(self) -> list[Path]:
        """List all regular files present in the job's local workspace.

        This implicitly invokes `get_local_folder()` to ensure the workspace
        is established before attempting to read its contents.

        Returns:
            list[Path]: An absolute list of file paths found in the directory.
        """
        # TODO: Make this recursive
        folder = self.get_local_folder()
        return [f for f in folder.iterdir() if f.is_file()]

    def get_tar(self, compression: str = "gz") -> tarfile.TarFile:
        """Generate a tarball archive containing all files in the local workspace.

        This method dynamically queries `get_filenames()` and writes those paths
        to an in-memory or temporary file-backed tarball. It resets the file
        pointer before returning, meaning the caller receives a ready-to-read
        archive handle.

        Args:
            compression (str): The tarfile compression scheme to apply. Supported
                modes include '' (none), 'gz' (gzip), 'bz2' (bzip2), and 'xz' (lzma).

        Returns:
            tarfile.TarFile: A tarfile object initialized in read mode (`r:*`).
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
    """A basic, concrete implementation of the abstract Job class.

    This class can be used as a standalone structural entity for testing queue
    logistics, but it drops all output artifacts by default.
    """

    def store_results(self, archive_path: Path) -> None:
        """Discard the results archive explicitly.

        As a default stub implementation, this method takes no action. If persistence
        is desired, a specialized Job subclass must be created to override it.

        Args:
            archive_path (Path): The ignored path to the generated results tarball.
        """
        pass


class Queue(ABC):
    """Abstract base class dictating the contract for managing a collection of jobs."""

    def __init__(self, job_class: type[Job] = QueuedJob) -> None:
        """Configure the baseline structure of the job queue.

        Args:
            job_class: The expected concrete class type for jobs that will be
                       pushed into this queue (defaults to `QueuedJob`).
        """
        self.job_class = job_class

    @abstractmethod
    def queue_job(self, job: Job) -> None:
        """Submit a new job instance into the active queue architecture.

        Args:
            job (Job): The unstarted job instance ready for tracking/execution.
        """
        pass  # pragma: no cover

    def jobs(self) -> Iterator[Job]:
        """Provide an active, lazy iterator over the current jobs in the queue.

        This relies on the abstract `all_jobs()` method to supply the source data,
        ensuring the queue can be iterated without necessarily loading all items
        into memory at once (depending on the subclass implementation).

        Yields:
            Job: Successive uncompleted jobs awaiting processing.
        """
        return iter(self.all_jobs())

    @abstractmethod
    def all_jobs(self) -> Iterable[Job]:
        """Retrieve the definitive set of all jobs currently tracked by the queue.

        Returns:
            Iterable[Job]: A traversable collection representing the queue's state.
        """
        pass  # pragma: no cover

    @abstractmethod
    def delete(self, job: Job) -> None:
        """Purge a completed or failed job from the queue's tracked state.

        Args:
            job (Job): The specific job instance to remove.
        """
        pass  # pragma: no cover


class LocalQueue(Queue):
    """A concrete Queue implementation that stores jobs within local memory."""

    def __init__(self, job_class: type[Job] = QueuedJob) -> None:
        """Initialize an empty, local memory-backed list for managing job tracking.

        Args:
            job_class: The expected class type for queued jobs.
        """
        super().__init__(job_class)
        self._jobs: list[Job] = []

    def queue_job(self, job: Job) -> None:
        """Append the given job sequentially to the internal Python list.

        Args:
            job (Job): The job to append.
        """
        self._jobs.append(job)

    def all_jobs(self) -> Iterable[Job]:
        """Return a snapshot of all active jobs currently in the local list.

        We return a fresh copy via `list()` to prevent mutation errors if the
        consumer iterates over the list while another thread/process deletes jobs.

        Returns:
            Iterable[Job]: A copy of the current internal job array.
        """
        return list(self._jobs)

    def delete(self, job: Job) -> None:
        """Erase a job from the internal list if it exists.

        Args:
            job (Job): The explicit job reference to match and remove.
        """
        if job not in self._jobs:
            return
        self._jobs.remove(job)
