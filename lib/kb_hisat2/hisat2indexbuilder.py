from __future__ import print_function
import subprocess
from util import (
    fetch_fasta_from_object
)

class Hisat2IndexManager(object):
    """
    Manages HISAT2 index files built from a FASTA file. Mainly, this constructs the indexes, or
    fetches them from SHOCK or a cache service as available.
    """

    def __init__(self, workspace_url, callback_url, working_dir):
        self.workspace_url = workspace_url
        self.callback_url = callback_url
        self.working_dir = working_dir

    def get_hisat2_index(self, source_ref):
        """
        Builds or fetches the index file(s) as necessary, unpacks them in a directory.
        Returns a dictionary with the following keys:
            index_dir = the directory with the index files
            prefix = the prefix of all files in that dir (to be used as input into HISAT2)
        """
        index_dir = self._fetch_hisat2_index({})
        if index_dir:
            return index_dir
        index_dir = self._build_hisat2_index(source_ref, {})

    def inspect_hisat2_index(self):
        pass

    def _build_hisat2_index(self, source_ref, options):
        """
        Runs hisat2-build to build the index files and directory for use in HISAT2.
        This also caches them, um, elsewhere so they can be found again.
        """
        # check options and raise ValueError here as needed.
        try:
            fasta_file = fetch_fasta_from_object(source_ref, self.workspace_url, self.callback_url)
            fasta_path = fasta_file.get("path", None)
            if fasta_path is None:
                raise RuntimeError("FASTA file fetched from object {} doesn't seem to exist!".format(source_ref))
            build_hisat2_cmd = [
                "hisat2-build",
                "-f"
            ]
            if options.get('num_threads', None) is not None:
                build_hisat2_cmd.extend(["-p", options['num_threads']])

        except ValueError as err:
            print("Incorrect object type for fetching a FASTA file!")

    def _fetch_hisat2_index(self, options):
        """
        Fetches HISAT2 indexes from a remote location, if they're available.
        """
        return None
