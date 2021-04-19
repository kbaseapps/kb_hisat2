"""
Module: hisat2indexmanager

This module handles manipulation of index files for HISAT2. The main use is as follows:
manager = Hisat2IndexManager(inputs)
idx_prefix = manager.get_hisat2_index(source_ref)

This will get onto the local filesystem (either from a datastore or by direct generation), the
HISAT2 index files from either a genome or assembly (or contigset) object. If generated, these
are also stored somewhere and associated with the genome ref.
"""


import os
import subprocess
import uuid

from kb_hisat2.file_util import fetch_fasta_from_object


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
        Returns a string representing the path and prefix of the index files.
        E.g. if there are a set of files like "foo.1.ht2", "foo.2.ht2", etc. all in the
        "my_reads" directory, this will return "my_reads/foo"
        """
        idx_prefix = self._fetch_hisat2_index(source_ref, {})
        if idx_prefix:
            return idx_prefix
        else:
            return self._build_hisat2_index(source_ref, {})

    def inspect_hisat2_index(self):
        pass

    def _build_hisat2_index(self, source_ref, options):
        """
        Runs hisat2-build to build the index files and directory for use in HISAT2.
        It creates a directory called "kb_hisat2_idx" and places the index files within.
        This also caches them, um, elsewhere so they can be found again.
        """
        # check options and raise ValueError here as needed.
        if source_ref is None:
            raise ValueError("Missing reference object needed to build a HISAT2 index.")
        print("Building HISAT2 index files for {}".format(source_ref))
        idx_dir = "kb_hisat2_idx"
        idx_prefix = "kb_hisat2_idx-" + str(uuid.uuid4())
        try:
            os.mkdir(os.path.join(self.working_dir, idx_dir))
        except OSError:
            print("Ignoring error for already existing {} directory".format(idx_dir))
        try:
            print("Fetching FASTA file from object {}".format(source_ref))
            fasta_file = fetch_fasta_from_object(source_ref, self.workspace_url, self.callback_url)
            print("Done fetching FASTA file! Path = {}".format(fasta_file.get("path", None)))
        except ValueError:
            print("Incorrect object type for fetching a FASTA file!")
            raise

        fasta_path = fasta_file.get("path", None)
        if fasta_path is None:
            raise RuntimeError("FASTA file fetched from object {} doesn't seem to "
                               "exist!".format(source_ref))
        build_hisat2_cmd = [
            "hisat2-build",
            "-f",
            fasta_path
        ]
        if options.get('num_threads', None) is not None:
            build_hisat2_cmd.extend(["-p", options['num_threads']])
        idx_prefix_path = os.path.join(self.working_dir, idx_dir, idx_prefix)
        build_hisat2_cmd.append(idx_prefix_path)
        print("Executing build-hisat2 command: {}".format(build_hisat2_cmd))
        p = subprocess.Popen(build_hisat2_cmd, shell=False)
        ret_code = p.wait()
        if ret_code != 0:
            raise RuntimeError('Failed to generate HISAT2 index files!')
        print("Done! HISAT2 index files created with prefix {}".format(idx_prefix_path))
        return idx_prefix_path

    def _fetch_hisat2_index(self, source_ref, options):
        """
        Fetches HISAT2 indexes from a remote location, if they're available.
        """
        # TODO: insert fetch code from file cache HERE.
        return None
