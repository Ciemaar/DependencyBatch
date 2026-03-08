# Dependency Batch

A modern, type-safe Python library for modeling and managing job queues and batch dependencies. This library provides abstract base classes and default implementations for jobs (`Job`, `QueuedJob`) and queues (`Queue`, `LocalQueue`), supporting file-based job data handling with secure tarball extraction.

## Requirements

- Python 3.12 or higher

## Installation

To install the library and its dependencies:

```bash
pip install -r requirements.txt
```

## Documentation

For comprehensive information on how to use and contribute to this project, please refer to the following guides:

- **[User Guide](docs/user_guide.md)**: Explains the core concepts, custom jobs, and queue management.
- **[Developer Guide](docs/developer_guide.md)**: Covers environment setup, testing, code quality tools, and CI/CD.

## Quick Start

### Creating a Custom Job

You can inherit from `Job` to create custom job types. The base `Job` class handles local file management and tarball creation/extraction.

```python
from dependency_batch import Job

class MyJob(Job):
    def get_filenames(self) -> list[str]:
        # Implement logic to return a list of file paths associated with the job
        return ["/path/to/file1.txt"]

    def get_tar(self, compression: str = "gz"):
        # You can override get_tar if needed, or use the default implementation
        return super().get_tar(compression)
```

### Using the Local Queue

`LocalQueue` is a concrete implementation of `Queue` that stores jobs in memory.

```python
from dependency_batch import LocalQueue, QueuedJob

# Create a queue
queue = LocalQueue()

# create a job
job = QueuedJob()

# Add a job to the queue
queue.queue_job(job)

# Process jobs
for job in queue.jobs():
    print(f"Processing job: {job}")

# Remove a job
queue.delete(job)
```

## Development

This project uses modern Python tooling for code quality and testing.

### Setup

1. Clone the repository.

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Running Tests

Run the test suite using `pytest`:

```bash
PYTHONPATH=. pytest
```

### Type Checking

Type checking is performed using `pyright`:

```bash
pyright .
```

### Linting and Formatting

Linting and formatting are handled by `ruff`:

```bash
ruff check .
ruff format .
```

## CI/CD

This project uses GitHub Actions for Continuous Integration. The workflow defined in `.github/workflows/ci.yml` runs `ruff`, `pyright`, and `pytest` on every push and pull request to the `main` or `master` branches.

## Future Work

- AWS Integration (S3 for storage, SQS for queues) is planned for future releases. Currently, only local file and memory-based implementations are provided.
