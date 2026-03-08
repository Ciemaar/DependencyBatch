import tarfile
import tempfile
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from model import Job, LocalQueue


class LocalJob(Job):
    """Job that starts with local files."""

    def __init__(self, files: dict[str, str] | None = None) -> None:
        super().__init__()
        self._initial_files = files or {}

    def get_local_folder(self) -> Path:
        if self.local_dir:
            return self.local_dir
        self.local_dir = Path(tempfile.mkdtemp())
        for name, content in self._initial_files.items():
            with open(self.local_dir / name, "w") as f:
                f.write(content)
        return self.local_dir


class ArchiveJob(Job):
    """Job that starts with a tarball."""

    def __init__(self, tar_content: bytes) -> None:
        super().__init__()
        self._tar_content = tar_content

    def get_tar(self, compression: str = "gz") -> tarfile.TarFile:
        fileobj = tempfile.TemporaryFile()  # noqa: SIM115
        fileobj.write(self._tar_content)
        fileobj.seek(0)
        return tarfile.open(fileobj=fileobj, mode="r:*")


def test_job_lifecycle() -> None:
    with LocalJob({"test.txt": "hello"}) as folder:
        assert (folder / "test.txt").exists()

        # Test get_filenames
        # Re-get the job object (we could yield the job instead,
        # but the request specifically asked for get_localfolder on enter)
        # Since we only have the folder path, we need to create the job again
        # Actually, let's keep the job instance available
        pass

    # The context manager exited, so the folder should be deleted
    assert not folder.exists()


def test_job_methods() -> None:
    job = LocalJob({"test.txt": "hello"})
    folder = job.get_local_folder()
    assert (folder / "test.txt").exists()

    # Test get_filenames
    filenames = job.get_filenames()
    assert len(filenames) == 1
    assert filenames[0].name == "test.txt"

    # Test get_tar
    tar = job.get_tar()
    assert isinstance(tar, tarfile.TarFile)
    members = tar.getmembers()
    assert len(members) == 1
    assert members[0].name == "test.txt"
    tar.close()

    # Test close
    job.close()
    assert not folder.exists()
    assert job.local_dir is None


def test_archive_job() -> None:
    # Create a tarball from a LocalJob
    job1 = LocalJob({"foo.txt": "bar"})
    tar1 = job1.get_tar()

    # Read the tar content
    # We need to access the underlying fileobj.
    # TarFile object doesn't expose the fileobj directly as a public attribute easily
    # in all versions, but usually `fileobj` attribute exists.
    assert tar1.fileobj is not None
    tar1.fileobj.seek(0)
    content = tar1.fileobj.read(-1)
    tar1.close()
    job1.close()

    # Create ArchiveJob
    job2 = ArchiveJob(content)
    folder2 = job2.get_local_folder()
    assert (folder2 / "foo.txt").exists()

    with open(folder2 / "foo.txt") as f:
        assert f.read() == "bar"

    filenames2 = job2.get_filenames()
    assert any(f.name == "foo.txt" for f in filenames2)
    job2.close()


def test_queue_operations() -> None:
    q = LocalQueue()
    job1 = LocalJob()
    job2 = LocalJob()

    q.queue_job(job1)
    assert len(q.allJobs()) == 1

    q.queue_job(job2)
    assert len(q.allJobs()) == 2

    # Test generator
    jobs = list(q.jobs())
    assert len(jobs) == 2
    assert job1 in jobs
    assert job2 in jobs

    q.delete(job1)
    assert len(q.allJobs()) == 1
    assert q.allJobs()[0] == job2


@given(st.lists(st.integers()))
def test_queue_hypothesis(items: list[int]) -> None:
    q = LocalQueue()
    jobs = []
    for i in items:
        j = LocalJob({"id": str(i)})
        q.queue_job(j)
        jobs.append(j)

    assert len(q.allJobs()) == len(items)

    # Test deletion
    if jobs:
        to_delete = jobs[0]
        q.delete(to_delete)
        assert len(q.allJobs()) == len(items) - 1
        assert to_delete not in q.allJobs()
