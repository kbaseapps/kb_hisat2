"""
hisat2.py - the core of the HISAT module.
-----------------------------------------
This does all the heavy lifting of running HISAT2 to align reads against a reference sequence.
It should be used as follows, mainly from kb_hisat2Impl.py.

Case 1 - A single sample of reads - either a PairedEndLibrary or SingleEndLibrary.
genome_idx = Hisat2.build_index(genome_ref)
reads_files = util.fetch_reads_from_sampleset(sampleset_ref)
alignments = Hisat2.run_hisat2(genome_idx, reads_files[0], input_params)

Case 2 - A set of reads - either a ReadsSet or a SampleSet.
(get genome idx and reads files as above, now reads_files is a list of samples.)
for reads in reads_files:
    alignments = Hisat2.run_hisat2(genome_idx, reads, input_params)

TODO: use the kb_parallel system to parallelize this.
"""
from __future__ import print_function
import subprocess
import os
from pprint import pprint
from kb_hisat2.hisat2indexmanager import Hisat2IndexManager

HISAT_VERSION = "2.0.5"


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

    def run_hisat2(self, idx_prefix, reads, input_params, output_file="aligned_reads"):
        """
        Runs HISAT2 on the data with the given parameters. Only operates on a single set of
        single-end or paired-end reads.

        If the input is a sample set of multiple samples, then it runs this in a loop
        against the indexed genome/assembly.

        Before this is run...
        1. the index file(s) should be present in the file system (in idx_prefix)
        2. the reads file(s) should be present in the file system, too (in self.working_dir/reads)

        idx_prefix = absolute path to index files, with the file prefix.
                     E.g. /kb/scratch/idx/genome_index.
        reads_params = list of dicts:
            style = "paired" or "single"
            file_fwd = file for single end reads or first (forward) file for paired end reads
            file_rev = second (reverse direction) file for paired end reads
        object_ref = ...something?
        input_params = original dictionary of inputs and parameters from the Narrative App. This
                       gets munged into HISAT2 flags.
        output_file = the file prefix (before ".sam") for the generated reads. Default =
                      "aligned_reads". Used for doing multiple alignments over a set of
                      reads (a ReadsSet or SampleSet).
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
        # figure out style, crash if conflict
        if style is None:
            style = reads["style"]
        if style != reads["style"]:
            raise ValueError("Can only align sets of reads of the same type in one operation "
                             "- only single end or paired end, not both.")
        files_fwd.append(reads["file_fwd"])
        if style == "paired":
            files_rev.append(reads["file_rev"])
        style = style.lower()
        print("Done!")

        # 2. Set up a list of parameters to feed into the command builder
        print("Building HISAT2 execution parameters...")
        exec_params = list()
        exec_params.extend(["-p", str(input_params.get('num_threads', 2))])
        if input_params.get("quality_score", None) is not None:
            exec_params.append("--" + input_params["quality_score"])
        if input_params.get("orientation", None) is not None:
            exec_params.append("--" + input_params["orientation"])
        if input_params.get("no_spliced_alignment", False):
            exec_params.append("--no-spliced-alignment")
        if input_params.get("transcriptome_mapping_only", False):
            exec_params.append("--transcriptome-mapping-only")
        if input_params.get("tailor_alignments", None) is not None:
            exec_params.append("--" + str(input_params["tailor_alignments"]))

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
                    str(input_params[param])
                ])
        print("Done!")
        print("Building HISAT2 command...")
        alignment_file = os.path.join(self.working_dir, "{}.sam".format(output_file))
        cmd = self._build_hisat2_cmd(idx_prefix,
                                     style,
                                     files_fwd,
                                     files_rev,
                                     alignment_file,
                                     exec_params)
        print("Done!")
        print("Starting HISAT2 with the following command:")
        print(cmd)
        p = subprocess.Popen(cmd, shell=False)
        ret_code = p.wait()
        if ret_code != 0:
            raise RuntimeError('Failed to execute HISAT2 alignment with the given parameters!')
        print("Done!")
        print("Assembling output object and report...")
        alignment_ref = self._upload_hisat2_alignment(input_params, reads, alignment_file)
        print("Done!")
        return alignment_ref

    def _upload_hisat2_alignment(self, input_params, reads_info, alignment_file):
        """
        Uploads the alignment file + metadata.
        This then returns the expected return dictionary from HISAT2.
        """
        align_upload_params = {
            "ws_id_or_name": input_params["ws_name"],
            "file_path": alignment_file,
            "library_type": reads_info["style"],  # single or paired end,
            "condition": "some_condition",
            "genome_id": input_params["genome_ref"],
            "read_sample_id": reads_info["object_ref"],
            "aligned_using": "hisat2",
            "aligner_version": HISAT_VERSION,
            "aligner_opts": input_params,
        }
        print("Uploading completed alignment")
        pprint(align_upload_params)
        alignment_ref = "new_alignment_ref"
        # TODO: insert ReadsAlignmentUtils.upload_alignment here.
        return alignment_ref

    def _build_hisat2_report(self, params):
        """
        Builds and uploads the HISAT2 report.
        """
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
                raise ValueError("When aligning paired-end reads, there must be equal amounts of "
                                 "reads files for each side.")
            cmd.extend([
                "-1",
                ",".join(files_fwd),
                "-2",
                ",".join(files_rev)
            ])
        else:
            raise ValueError("HISAT2 run style must be one of 'paired' or 'single'. '{}' is not "
                             "allowed".format(style))

        cmd.extend(exec_params)
        cmd.extend([
            "-S",
            output_file
        ])
        return cmd
