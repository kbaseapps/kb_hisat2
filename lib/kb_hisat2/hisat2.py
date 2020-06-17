"""
hisat2.py - the core of the HISAT module.
-----------------------------------------
This does all the heavy lifting of running HISAT2 to align reads against a reference sequence.
"""
from __future__ import print_function

import os
import re
import subprocess
import uuid
from pipes import quote  # deprecated, but useful here for filenames
from pprint import pprint

from installed_clients.KBParallelClient import KBParallel
from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsAlignmentUtilsClient import ReadsAlignmentUtils
from installed_clients.SetAPIServiceClient import SetAPI
from installed_clients.kb_QualiMapClient import kb_QualiMap
from kb_hisat2.hisat2indexmanager import Hisat2IndexManager
from kb_hisat2.file_util import fetch_reads_from_reference
from kb_hisat2.util import package_directory, is_set, get_object_names

HISAT_VERSION = "2.1.0"


class Hisat2(object):
    def __init__(self, callback_url, srv_wiz_url, workspace_url, working_dir, provenance):
        self.callback_url = callback_url
        self.srv_wiz_url = srv_wiz_url
        self.workspace_url = workspace_url
        self.working_dir = working_dir
        self.provenance = provenance
        self.my_version = 'release'
        if provenance and len(provenance) > 0:
            if 'subactions' in provenance[0]:
                self.my_version = self.__get_version_from_subactions('kb_hisat2', provenance[0]['subactions'])
        print('Running kb_hisat2 version = ' + self.my_version)

    def __get_version_from_subactions(self, module_name, subactions):
        # go through each sub action looking for
        if not subactions:
            return 'release'  # default to release if we can't find anything
        for sa in subactions:
            if 'name' in sa:
                if sa['name'] == module_name:
                    # local-docker-image implies that we are running in kb-test, so return 'dev'
                    if sa['commit'] == 'local-docker-image':
                        return 'dev'
                    # to check that it is a valid hash, make sure it is the right
                    # length and made up of valid hash characters
                    if re.match('[a-fA-F0-9]{40}$', sa['commit']):
                        return sa['commit']
        # again, default to setting this to release
        return 'release'

    def build_index(self, object_ref):
        """
        Uses the Hisat2IndexManager to build/retrieve the HISAT2 index files
        based on the object ref.
        """
        idx_manager = Hisat2IndexManager(self.workspace_url, self.callback_url, self.working_dir)
        return idx_manager.get_hisat2_index(object_ref)

    def run_single(self, reads_ref, params):
        """
        Performs a single run of HISAT2 against a single reads reference. The rest of the info
        is taken from the params dict - see the spec for details.
        """
        # 1. Get hisat2 index from genome.
        #    a. If it exists in cache, use that.
        #    b. Otherwise, build it
        idx_prefix = self.build_index(params["genome_ref"])

        # 2. Fetch the reads file and deal make sure input params are correct.
        reads = fetch_reads_from_reference(reads_ref["ref"], self.callback_url)
        # if the reads ref came from a different sample set, then we need to drop that
        # reference inside the reads info object so it can be linked in the alignment
        if reads_ref["ref"] != params["sampleset_ref"]:
            reads["sampleset_ref"] = params["sampleset_ref"]
        # make sure condition info carries over if we have it
        if "condition" in reads_ref:
            reads["condition"] = reads_ref["condition"]
        elif "condition" in params:
            reads["condition"] = params["condition"]
        reads["name"] = reads_ref["name"]
        output_file = "accepted_hits"

        # 3. Finally all set, do the alignment and upload the output.
        alignment_file = self.run_hisat2(
            idx_prefix, reads, params, output_file=output_file
        )
        alignment_name = reads["name"] + params["alignment_suffix"]
        output_ref = self.upload_alignment(params, reads, alignment_name, alignment_file)
        alignment_set_ref = None
        if is_set(params["sampleset_ref"], self.workspace_url):
            # alignment_items, alignmentset_name, ws_name
            set_name = get_object_names([params["sampleset_ref"]], self.workspace_url)[params["sampleset_ref"]]
            alignment_set_name = set_name + params["alignmentset_suffix"]
            alignment_set_ref = self.upload_alignment_set(
                [{
                    "ref": output_ref,
                    "label": reads["condition"]
                }],
                alignment_set_name,
                params["ws_name"]
            )
        alignments = dict()
        alignments[reads_ref["ref"]] = {
            "ref": output_ref,
            "name": alignment_name
        }
        os.remove(reads["file_fwd"])
        if "file_rev" in reads:
            os.remove(reads["file_rev"])
        return (alignments, output_ref, alignment_set_ref)

    def run_batch(self, reads_refs, params):
        """
        Runs HISAT2 in batch mode.
        reads_refs should be a list of dicts, where each looks like the following:
        {
            "ref": reads object reference,
            "condition": condition for that ref (string)
        }
        """
        # build task list and send it to KBParallel
        tasks = list()
        set_name = get_object_names([params["sampleset_ref"]], self.workspace_url)[params["sampleset_ref"]]
        for idx, reads_ref in enumerate(reads_refs):
            single_param = dict(params)  # need a copy of the params
            single_param["build_report"] = 0
            single_param["sampleset_ref"] = reads_ref["ref"]
            if "condition" in reads_ref:
                single_param["condition"] = reads_ref["condition"]
            else:
                single_param["condition"] = "unspecified"

            tasks.append({
                "module_name": "kb_hisat2",
                "function_name": "run_hisat2",
                "version": self.my_version,
                "parameters": single_param
            })
        # UNCOMMENT BELOW FOR LOCAL TESTING
        batch_run_params = {
            "tasks": tasks,
            "runner": "parallel",
            # "concurrent_local_tasks": 3,
            # "concurrent_njsw_tasks": 0,
            "max_retries": 2
        }
        parallel_runner = KBParallel(self.callback_url)
        results = parallel_runner.run_batch(batch_run_params)["results"]
        alignment_items = list()
        alignments = dict()
        for idx, result in enumerate(results):
            # idx of the result is the same as the idx of the inputs AND reads_refs
            if result["is_error"] != 0:
                raise RuntimeError("Failed a parallel run of HISAT2! {}".format(result["result_package"]["error"]))
            reads_ref = tasks[idx]["parameters"]["sampleset_ref"]
            alignment_items.append({
                "ref": result["result_package"]["result"][0]["alignment_objs"][reads_ref]["ref"],
                "label": reads_refs[idx].get(
                    "condition",
                    params.get("condition",
                               "unspecified"))
            })
            alignments[reads_ref] = result["result_package"]["result"][0]["alignment_objs"][reads_ref]
        # build the final alignment set
        output_ref = self.upload_alignment_set(
            alignment_items, set_name + params["alignmentset_suffix"], params["ws_name"]
        )
        return (alignments, output_ref)

    def run_hisat2(self, idx_prefix, reads, input_params, output_file="accepted_hits"):
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
                      "accepted_hits". Used for doing multiple alignments over a set of
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

    # def upload_alignment_set(self, input_params, alignment_info, reads_info, alignmentset_name):
    def upload_alignment_set(self, alignment_items, alignmentset_name, ws_name):
        """
        Compiles and saves a set of alignment references (+ other stuff) into a
        KBaseRNASeq.RNASeqAlignmentSet.
        Returns the reference to the new alignment set.

        alignment_items: [{
            "ref": alignment_ref,
            "label": condition label.
        }]
        # alignment_info = dict like this:
        # {
        #     reads_ref: {
        #         "ref": alignment_ref
        #     }
        # }
        # reads_info = dict like this:
        # {
        #     reads_ref: {
        #         "condition": "some condition"
        #     }
        # }
        # input_params = global input params to HISAT2, also has ws_name for the target workspace.
        # alignmentset_name = name of final set object.
        """
        print("Uploading completed alignment set")
        alignment_set = {
            "description": "Alignments using HISAT2, v.{}".format(HISAT_VERSION),
            "items": alignment_items
        }
        set_api = SetAPI(self.srv_wiz_url)
        set_info = set_api.save_reads_alignment_set_v1({
            "workspace": ws_name,
            "output_object_name": alignmentset_name,
            "data": alignment_set
        })
        return set_info["set_ref"]

    def upload_alignment(self, input_params, reads_info, alignment_name, alignment_file):
        """
        Uploads the alignment file + metadata.
        This then returns the expected return dictionary from HISAT2.
        """
        aligner_opts = dict()
        for k in input_params:
            aligner_opts[k] = str(input_params[k])

        align_upload_params = {
            "destination_ref": "{}/{}".format(input_params["ws_name"], alignment_name),
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

        qm = kb_QualiMap(self.callback_url, service_ver='dev')
        qc_ref = alignment_set
        if qc_ref is None:  # then there's only one alignment...
            qc_ref = alignments[alignments.keys()[0]]["ref"]
        bamqc_params = {
            "create_report": 0,
            "input_ref": qc_ref
        }
        result = qm.run_bamqc(bamqc_params)
        index_file = None
        for f in os.listdir(result["qc_result_folder_path"]):
            if f.endswith(".html"):
                index_file = f
        if index_file is None:
            raise RuntimeError("QualiMap failed - no HTML file was found in the generated output.")
        html_zipped = package_directory(self.callback_url,
                                        result["qc_result_folder_path"],
                                        index_file,
                                        'QualiMap Results')
        report_params = {
            "message": report_text,
            "direct_html_link_index": 0,
            "html_links": [html_zipped],
            "report_object_name": "QualiMap-" + str(uuid.uuid4()),
            "workspace_name": params["ws_name"],
            "objects_created": created_objects
        }

        report_info = report_client.create_extended_report(report_params)
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
