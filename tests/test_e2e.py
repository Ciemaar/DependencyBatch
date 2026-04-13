import tarfile
import typing
from pathlib import Path

import pytest

from dependency_batch import Job, LocalQueue


class DataProcessingJob(Job):
    """An E2E job that processes an input file and produces an output file."""

    def __init__(self, input_data: str, storage_dir: Path | None = None) -> None:
        super().__init__()
        self.input_data = input_data
        self.storage_dir = storage_dir
        self.stored_archive: Path | None = None

    def execute(self) -> None:
        """Simulates processing work."""
        folder = self.get_local_folder()

        # Write input data to workspace
        input_file = folder / "input.txt"
        input_file.write_text(self.input_data)

        # Process data (e.g. uppercase it)
        output_data = self.input_data.upper()

        # Write output file
        output_file = folder / "output.txt"
        output_file.write_text(output_data)

        # Mark output file as a result to be archived
        self.results.add(output_file)

    def store_results(self, archive_path: Path) -> None:
        """Stores the resulting tarball."""
        if self.storage_dir:
            # "Real" storage: move the archive to the final destination
            final_path = self.storage_dir / archive_path.name
            import shutil

            shutil.copy2(archive_path, final_path)
            self.stored_archive = final_path
        else:
            # "Mock" storage: just record that we received it
            # The base Job class will delete the temporary archive afterward.
            pass


def test_e2e_workflow(tmp_path: Path, request: pytest.FixtureRequest) -> None:
    """E2E workflow: queues jobs, processes them, and stores results."""
    no_mocks = request.config.getoption("--no-mocks")

    storage_dir = tmp_path / "storage"
    if no_mocks:
        storage_dir.mkdir()
    else:
        storage_dir = None

    queue = LocalQueue()

    # Queue multiple jobs
    job1 = DataProcessingJob("hello world", storage_dir=storage_dir)
    job2 = DataProcessingJob("e2e testing", storage_dir=storage_dir)

    queue.queue_job(job1)
    queue.queue_job(job2)

    # Process jobs
    for job in queue.jobs():
        # Because we need the execute method and we're type-hinted to the base Job,
        # we'll cast it to our custom class for the test.
        dj = typing.cast(DataProcessingJob, job)

        # Using the context manager ensures `close()` is called,
        # which triggers `handle_results()` and `store_results()`.
        with dj:
            dj.execute()

        queue.delete(job)

    assert len(list(queue.all_jobs())) == 0

    if no_mocks:
        # Verify real storage
        assert storage_dir is not None
        assert job1.stored_archive is not None and job1.stored_archive.exists()
        assert job2.stored_archive is not None and job2.stored_archive.exists()

        # Verify archive contents
        with tarfile.open(job1.stored_archive, "r:gz") as tar:
            members = tar.getnames()
            assert "output.txt" in members

            # Extract and verify the content
            member = tar.extractfile("output.txt")
            assert member is not None
            content = member.read().decode("utf-8")
            assert content == "HELLO WORLD"
