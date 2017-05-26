from hisat2indexmanager import Hisat2IndexManager

class Hisat2(object):
    def __init__(self, callback_url, workspace_url, working_dir):
        self.callback_url = callback_url
        self.workspace_url = workspace_url
        self.working_dir = working_dir

    def build_index(self, object_ref):
        """
        Uses the Hisat2IndexManager to build/retrieve the HISAT2 index files
        based on the object ref.
        """
        idx_manager = Hisat2IndexManager(self.workspace_url, self.callback_url, self.working_dir)
        return idx_manager.get_hisat2_index(object_ref)

    def run_hisat2(self, idx_prefix, object_ref, reads_params, exec_params):
        """
        Runs HISAT2 on the data with the given parameters.
        If the input is a sample set of multiple samples, then it runs this in a loop
        against the indexed genome/assembly.

        Before this is run...
        1. the index file(s) should be present in the file system (in self.working_dir/idx_prefix)
        2. the reads file(s) should be present in the file system as well (in self.working_dir/reads)

        reads_params = list of dicts:
            style = "paired" or "single"
            file1 = file for single end reads or first file for paired end reads
            file2 = second file for single end reads
        """

        # from the inputs, we need the sets of reads.
        # cases:
        #   KBaseSets.ReadsSet             - one or more PairedEndLibary or SingleEndLibrary
        #   KBaseRNASeq.RNASeqSampleSet    - one or more single or paired reads set input
        #   KBaseAssembly.SingleEndLibrary - one reads set input
        #   KBaseAssembly.PairedEndLibrary - one paired reads set input
        #   KBaseFile.SingleEndLibrary     - one reads set input
        #   KBaseFile.PairedEndLibrary     - one paired reads set input



    def _build_hisat2_cmd(self, idx_prefix, style, files, files_paired):
        """
        idx_prefix = file prefix of the index files.
        style = one of "paired" or "single"
        files = list of file names
        files_paired = list of paired file names in the case of paired-end reads. Note that this
                       *MUST* be the same length as the first files list, and each element
                       corresponds to the pairing element from the other list.
        examples:
        _build_hisat2_cmd("foo", "single", ["file1.fq", "file2.fq"])
        _build_hisat2_cmd("bar", "paired", ["fileA_1.fq", "fileB_1.fq"], ["fileA_2.fq", "fileB_2.fq"])
        """
        cmd = [
            'hisat2',
            '-x',
            idx_prefix
        ]

        if style == "single":
            cmd.append("-U")
            cmd.append(",".join(files))
        elif style == "paired":
            if len(files) != len(files_paired):
                raise ValueError("When aligning paired-end reads, there must be equal amounts of reads files for each side.")
            cmd.extend([
                "-1",
                ",".join(files),
                "-2",
                ",".join(files_paired)
            ])
        else:
            raise ValueError("HISAT2 run style must be one of 'paired' or 'single'")

        cmd.extend([
            "-S",
            "hisat2_alignments"
        ])
