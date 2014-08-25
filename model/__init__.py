from os import tmpfile, tmpnam, listdir, makedirs, rmdir
import os.path
import tarfile

class Job(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        super().__init__()
        self.depends_on = []
        self.result_of = []
        self.results = []
        self.local_dir = None

    def close(self):
        """Cleanup any local files and close the job.


        """
        for filename in self.get_filenames():
            unlink(filename)
        rmdir(self.local_dir)

    def get_local_folder(self):
        """Get a local folder with the files of this job

        The base class implementation of this method assumes that get_tar() is implemented and can be used to get the data
        :return:
        """
        self.local_dir = tmpnam()
        makedirs(self.local_dir)
        self.get_tar().extract_all(self.local_dir)
        return self.local_dir

    def get_filenames(self):
        """Get the local filenames for this Job retrieving if necessary

        The base class assumes that get_local_folder() is implemented and can be used to get the folder to check
        :return: str
        """
        #TODO: Make this recursive
        return listdir(self.get_local_folder())

    def get_tar(self, compression="gz"):
        """Get the data related to this job as a tar file object

        The base class assumes that get_filenames() is implemented and can be used to get the files to pack

           compression:

           ''         no compression/automatic compression
           'gz'       gzip compression
           'bz2'      bzip2 compression
           'xz'       lzma compression

           :return: tarfile.TarFile
        """
        mode = 'w:'+compression
        tfile = tarfile.open(fileobj=tmpfile(), mode=mode)
        for file in self.get_filenames()
            tfile.add(file, arcname=file, recursive=True)
        tfile.close()
        tfile
        return tarFileObj



class Queue(object):
    __metaclass__ = ABCMeta

    def __init__(self, job_class=QueuedJob):
        self.openJobs = {}
        self.job_class = job_class

    @abstractmethod
    def queue_job(self, job):
        """
        Add the given job to this queue
        """
        pass

    def jobs(self):
        """
        A generator that returns jobs
        the same job will not be returned twice by the
        same queue object
        """
        return iter(self.allJobs())

    @abstractmethod
    def allJobs(self):
        pass

    @abstractmethod
    def delete(self, job):
        pass
