# User Guide

This guide explains how to use the `model` library to manage jobs and job queues in your Python applications.

## Core Concepts

The library is built around two main abstract base classes:

1. **`Job`**: Represents a single unit of work. It encapsulates data associated with the job (files, dependencies, results) and provides methods to manage its local environment and package its data into a tar archive.
1. **`Queue`**: Represents a mechanism to store, retrieve, and manage `Job` objects.

## Using Jobs

The `Job` base class provides infrastructure for handling local files.

### The Default `QueuedJob`

The simplest way to use a job is the default `QueuedJob` class, which is a concrete implementation of `Job`.

```python
from model import QueuedJob

job = QueuedJob()
# You can now use the job instance
```

### Creating Custom Jobs

To implement specific logic, you should inherit from `Job`.

#### Managing Files

When a job needs to work with local files, it uses a local folder. You can implement the `get_filenames` method to specify which files belong to this job.

```python
from model import Job
import os

class MyAnalysisJob(Job):
    def __init__(self, data_file: str):
        super().__init__()
        self.data_file = data_file

    def get_filenames(self) -> list[str]:
        # Return the list of files associated with this job
        return [self.data_file]
```

#### Archiving Job Data

The `Job` class automatically handles archiving the job's files into a tarball. By default, calling `job.get_tar()` will:

1. Call `self.get_filenames()` to see what needs archiving.
1. Create a temporary gzip-compressed tarball containing those files.
1. Return a `tarfile.TarFile` object opened for reading.

```python
# Assuming MyAnalysisJob from above
job = MyAnalysisJob("data/input.csv")
tar_archive = job.get_tar()

# Read from the archive
for member in tar_archive.getmembers():
    print(f"Archived file: {member.name}")

tar_archive.close()
```

#### Working with Archived Jobs

If a job is initialized from an existing archive (e.g., downloaded from a remote server), calling `job.get_local_folder()` will automatically extract the tarball into a secure temporary directory.

```python
# Assuming 'job' was created from a remote tarball
local_dir = job.get_local_folder()
print(f"Job files extracted to: {local_dir}")
# ... process files in local_dir ...

# Clean up when done
job.close()
```

## Using Queues

### The `LocalQueue`

The `LocalQueue` is an in-memory queue implementation provided by the library.

```python
from model import LocalQueue, QueuedJob

# 1. Initialize the queue
queue = LocalQueue()

# 2. Create jobs
job1 = QueuedJob()
job2 = QueuedJob()

# 3. Add jobs to the queue
queue.queue_job(job1)
queue.queue_job(job2)

# 4. List all jobs in the queue
all_jobs = queue.allJobs()
print(f"Total jobs: {len(all_jobs)}")

# 5. Process jobs using the iterator
for job in queue.jobs():
    print("Processing a job...")
    # ... perform work ...

    # 6. Delete the job once finished
    queue.delete(job)
```

## Advanced Features

### Dependencies

The `Job` class includes `depends_on` and `result_of` attributes (lists of `Job` objects). While the base `Queue` implementations do not automatically resolve dependency graphs, you can use these attributes to build your own task orchestration logic.

### Results

You can store the output of a job in the `results` list attribute. This is simply an empty Python `list` initialized on the `Job` object. The base library does not include any methods that automatically read from or write to this list; it is provided purely as a convenient container for your custom subclasses or orchestration logic to store output data (like parsed metrics or status dictionaries).

## Security Note

The `Job.get_local_folder` method securely extracts tar archives using `filter="data"` to prevent directory traversal attacks (TarSlip). This feature requires Python 3.12 or higher.
