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
from pipes import quote  # deprecated, but useful here for filenames
from kb_hisat2.hisat2indexmanager import Hisat2IndexManager
from ReadsAlignmentUtils.ReadsAlignmentUtilsClient import ReadsAlignmentUtils
from KBaseReport.KBaseReportClient import KBaseReport
from Workspace.WorkspaceClient import Workspace
from SetAPI.SetAPIClient import SetAPI

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
        return alignment_file
        print("Assembling output object and report...")
        alignment_ref = self._upload_hisat2_alignment(input_params, reads, alignment_file)
        print("Done!")
        return alignment_ref

    def upload_alignment_set(self, input_params, alignment_info, reads_info, alignmentset_name):
        """
        Compiles and saves a set of alignment references (+ other stuff) into a
        KBaseRNASeq.RNASeqAlignmentSet.
        Returns the reference to the new alignment set.
        """
        print("Uploading completed alignment set")
        aligner_opts = dict()
        for k in input_params:
            aligner_opts[k] = str(input_params[k])

        alignment_items = list()
        for ref in alignment_info:
            alignment_items.append({
                "ref": alignment_info[ref]["ref"],
                "label": reads_info[ref].get("condition", None)
            })
        alignment_set = {
            "description": "Alignments using HISAT2, v.{}".format(HISAT_VERSION),
            "items": alignment_items
        }
        set_api = SetAPI(self.callback_url)
        set_info = set_api.save_reads_alignment_set_v1({
            "workspace": input_params["ws_name"],
            "output_object_name": alignmentset_name,
            "data": alignment_set
        })
        return set_info["set_ref"]

        # # the first 3 are parallel: reads_ref_list[i], condition_list[i], and alignment_list[i]
        # # all refer to the same reads ref
        # reads_ref_list = list()
        # condition_list = list()
        # alignment_list = list()
        # reads_alignments_ref_map_list = list()
        # reads_alignments_name_map_list = list()
        #
        # for ref in alignment_info:
        #     reads_ref_list.append(ref)
        #     condition_list.append(reads_info[ref].get("condition", None))
        #     alignment_list.append(alignment_info[ref]["ref"])
        #     reads_alignments_ref_map_list.append({ref: alignment_info[ref]["ref"]})
        #     reads_alignments_name_map_list.append({
        #         reads_info[ref]["name"]: alignment_info[ref]["name"]
        #     })
        #
        # alignment_set = {
        #     "aligned_using": "hisat2",
        #     "aligner_version": HISAT_VERSION,
        #     "sampleset_id": input_params['sampleset_ref'],
        #     "genome_id": input_params['genome_ref'],
        #     "aligner_opts": aligner_opts,
        #     "bowtie2_index": "",
        #     "read_sample_ids": reads_ref_list,
        #     "condition": condition_list,
        #     "sample_alignments": alignment_list,
        #     "mapped_rnaseq_alignments": reads_alignments_name_map_list,
        #     "mapped_alignments_ids": reads_alignments_ref_map_list
        # }
        # provenance = [{
        #     "input_ws_objects": alignment_list,
        #     "service": "kb_hisat2",
        #     "method": "run_hisat2"
        # }]
        #
        # print("Uploading completed alignment set with these parameters:")
        # as_obj = {
        #     "type": "KBaseRNASeq.RNASeqAlignmentSet",
        #     "data": alignment_set,
        #     "name": alignmentset_name,
        #     "provenance": provenance
        # }
        # pprint(as_obj)
        # ws = Workspace(self.workspace_url)
        # as_info = ws.save_objects({
        #     "workspace": input_params["ws_name"],
        #     "objects": [as_obj],
        # })[0]
        # return "{}/{}/{}".format(as_info[6], as_info[0], as_info[4])

    def upload_alignment(self, input_params, reads_info, alignment_file):
        """
        Uploads the alignment file + metadata.
        This then returns the expected return dictionary from HISAT2.
        """
        aligner_opts = dict()
        for k in input_params:
            aligner_opts[k] = str(input_params[k])

        align_upload_params = {
            "destination_ref": "{}/{}".format(input_params["ws_name"], input_params["alignmentset_name"]),
            "file_path": alignment_file,
            "library_type": reads_info["style"],  # single or paired end,
            "condition": reads_info["condition"],
            "assembly_or_genome_ref": input_params["genome_ref"],
            "read_library_ref": reads_info["object_ref"],
            "aligned_using": "hisat2",
            "aligner_version": HISAT_VERSION,
            "aligner_opts": aligner_opts
        }
        if "sampleset_ref" in reads_info:
            align_upload_params["sampleset_ref"] = reads_info["sampleset_ref"]
        print("Uploading completed alignment")
        pprint(align_upload_params)

        ra_util = ReadsAlignmentUtils(self.callback_url, service_ver="dev")
        alignment_ref = ra_util.upload_alignment(align_upload_params)["obj_ref"]
        print("Done! New alignment uploaded as object {}".format(alignment_ref))
        return alignment_ref

    def build_report(self, params, reads_refs, alignments, alignment_set=None):
        """
        Builds and uploads the HISAT2 report.
        """
        report_client = KBaseReport(self.callback_url)
        report_text = None
        created_objects = list()
        for k in alignments:
            created_objects.append({
                "ref": alignments[k]["ref"],
                "description": "Reads {} aligned to Genome {}".format(k, params["genome_ref"])
            })
        if alignment_set is not None:
            created_objects.append({
                "ref": alignment_set,
                "description": "Set of all new alignments"
            })

        report_text = "Created {} alignments from the given alignment set.".format(len(alignments))
        report_info = report_client.create({
            "workspace_name": params["ws_name"],
            "report": {
                "objects_created": created_objects,
                "text_message": report_text
            }
        })
        return report_info

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
        if style == "single" or style == "interleaved":
            cmd.extend([
                "-U",
                quote(",".join(files_fwd))
            ])
        elif style == "paired":
            if len(files_fwd) != len(files_rev):
                raise ValueError("When aligning paired-end reads, there must be equal amounts of "
                                 "reads files for each side.")
            cmd.extend([
                "-1",
                quote(",".join(files_fwd)),
                "-2",
                quote(",".join(files_rev))
            ])
        else:
            raise ValueError("HISAT2 run style must be 'paired', 'single', or 'interleaved'. "
                             "'{}' is not allowed".format(style))

        cmd.extend(exec_params)
        cmd.extend([
            "-S",
            quote(output_file)
        ])
        return cmd
