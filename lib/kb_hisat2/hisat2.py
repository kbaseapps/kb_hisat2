from __future__ import print_function
import subprocess
from kb_hisat2.hisat2indexmanager import Hisat2IndexManager


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

    def run_hisat2(self, idx_prefix, object_ref, reads_params, input_params):
        """
        Runs HISAT2 on the data with the given parameters.
        If the input is a sample set of multiple samples, then it runs this in a loop
        against the indexed genome/assembly.

        Before this is run...
        1. the index file(s) should be present in the file system (in self.working_dir/idx_prefix)
        2. the reads file(s) should be present in the file system, too (in self.working_dir/reads)

        reads_params = list of dicts:
            style = "paired" or "single"
            file_fwd = file for single end reads or first (forward) file for paired end reads
            file_rev = second (reverse direction) file for paired end reads
        object_ref = ...something?
        input_params = original dictionary of inputs and parameters from the Narrative App. This
                       gets munged into HISAT2 flags.
        """
        # from the inputs, we need the sets of reads.
        # cases:
        #   KBaseSets.ReadsSet             - one or more PairedEndLibary or SingleEndLibrary
        #   KBaseRNASeq.RNASeqSampleSet    - one or more single or paired reads set input
        #   KBaseAssembly.SingleEndLibrary - one reads set input
        #   KBaseAssembly.PairedEndLibrary - one paired reads set input
        #   KBaseFile.SingleEndLibrary     - one reads set input
        #   KBaseFile.PairedEndLibrary     - one paired reads set input

        print("Starting run_hisat2 function.")

        # 1. Set up the file lists and style (paired vs single)
        style = None
        files_fwd = list()
        files_rev = list()
        print("Building reads file parameters...")
        for reads in reads_params:
            # figure out style, crash if conflict
            if style is None:
                style = reads["style"]
            if style != reads["style"]:
                raise ValueError("Can only align sets of reads of the same type in one operation - only single end or paired end, not both.")
            files_fwd.append(reads["file_fwd"])
            if style == "paired":
                files_rev.append(reads["file_rev"])
        print("Done!")

        # 2. Set up a list of parameters to feed into the command builder
        print("Building HISAT2 execution parameters...")
        exec_params = list()
        exec_params.extend(["-p", input_params.get('num_threads', 2)])
        if input_params.get("quality_score", None) is not None:
            exec_params.append("--" + input_params["quality_score"])
        if input_params.get("orientation", None) is not None:
            exec_params.append("--" + input_params["orientation"])
        if input_params.get("no_spliced_alignment", False):
            exec_params.append("--no-spliced-alignment")
        if input_params.get("transcriptome_mapping_only", False):
            exec_params.append("--transcriptome-mapping-only")
        if input_params.get("tailor_alignments", None) is not None:
            exec_params.append("--" + input_params["tailor_alignments"])

        kbase_hisat_params = {
            "skip": "--skip",
            "trim3": "--trim3",
            "trim5": "--trim5",
            "np": "--np",
            "minins": "--minins",
            "maxins": "--maxins",
            "min_intron_length": "--min-intronlen",
            "max_intron_length": "--max-intronlen",
        }
        for param in kbase_hisat_params:
            if input_params.get(param, None) is not None:
                exec_params.extend([
                    kbase_hisat_params[param],
                    input_params[param]
                ])
        print("Done!")
        print("Building HISAT2 command...")
        cmd = self._build_hisat2_cmd(idx_prefix,
                                     style,
                                     files_fwd,
                                     files_rev,
                                     "aligned_reads.sam",
                                     exec_params)
        print("Done!")
        print("Starting HISAT2 with the following command:")
        print(cmd)
        p = subprocess.Popen(cmd)
        ret_code = p.wait()
        if ret_code != 0:
            raise RuntimeError('Failed to execute HISAT2 alignment with the given parameters!')
        print("Done!")
        print("Assembling output object and report...")
        self._build_hisat2_output()
        print("Done!")

    def _build_hisat2_output(self):
        pass

    def _build_hisat2_cmd(self, idx_prefix, style, files_fwd, files_rev, output_file, exec_params):
        """
        idx_prefix = file prefix of the index files.
        style = one of "paired" or "single"
        files_fwd = list of file names
        files_rev = list of paired file names in the case of paired-end reads. Note that this
                       *MUST* be the same length as the first files list, and each element
                       corresponds to the pairing element from the other list.
        examples:
        _build_hisat2_cmd("foo", "single", ["file1.fq", "file2.fq"])
        _build_hisat2_cmd("z", "paired", ["fileA_1.fq", "fileB_1.fq"], ["fileA_2.fq", "fileB_2.fq"])
        """
        cmd = [
            'hisat2',
            '-x',
            idx_prefix
        ]

        if style == "single":
            cmd.extend([
                "-U",
                ",".join(files_fwd)
            ])
        elif style == "paired":
            if len(files_fwd) != len(files_rev):
                raise ValueError("When aligning paired-end reads, there must be equal amounts of reads files for each side.")
            cmd.extend([
                "-1",
                ",".join(files_fwd),
                "-2",
                ",".join(files_rev)
            ])
        else:
            raise ValueError("HISAT2 run style must be one of 'paired' or 'single'")

        cmd.extend(exec_params)
        cmd.extend([
            "-S",
            output_file
        ])
        return cmd
