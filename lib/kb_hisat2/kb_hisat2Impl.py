# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
from __future__ import print_function
import os
from util import (
    check_hisat2_parameters,
)
from file_util import (
    fetch_reads_from_reference,
    fetch_reads_refs_from_sampleset
)
from kb_hisat2.hisat2 import Hisat2
from KBParallel.KBParallelClient import KBParallel
from pprint import pprint
#END_HEADER


class kb_hisat2:
    '''
    Module Name:
    kb_hisat2

    Module Description:
    A KBase module: kb_hisat2
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/briehl/kb_hisat2"
    GIT_COMMIT_HASH = "1e57d0568cbf3fe295cb5f0346784bc0c4ceac9e"

    #BEGIN_CLASS_HEADER
    # Class variables and functions can be defined in this block
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR

        # Any configuration parameters that are important should be parsed and
        # saved in the constructor.
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.workspace_url = config['workspace-url']
        self.shared_folder = config['scratch']
        self.num_threads = 2

        #END_CONSTRUCTOR
        pass


    def run_hisat2(self, ctx, params):
        """
        :param params: instance of type "Hisat2Params" (Input for hisat2.
           ws_name = the workspace name provided by the narrative for storing
           output. sampleset_ref = the workspace reference for the sampleset
           of reads to align. genome_ref = the workspace reference for the
           reference genome that HISAT2 will align against. alignmentset_name
           = the name of the alignment set object to create. num_threads =
           the number of threads to tell hisat to use (NOT USER SET?)
           quality_score = one of phred33 or phred64 skip = trim3 = trim5 =
           np = minins = maxins = orientation = min_intron_length =
           max_intron_length = no_spliced_alignment =
           transcriptome_mapping_only = tailor_alignments = condition = a
           string stating the experimental condition of the reads. REQUIRED
           for single reads, ignored for sets.) -> structure: parameter
           "ws_name" of String, parameter "alignmentset_name" of String,
           parameter "sampleset_ref" of String, parameter "condition" of
           String, parameter "genome_ref" of String, parameter "num_threads"
           of Long, parameter "quality_score" of String, parameter "skip" of
           Long, parameter "trim3" of Long, parameter "trim5" of Long,
           parameter "np" of Long, parameter "minins" of Long, parameter
           "maxins" of Long, parameter "orientation" of String, parameter
           "min_intron_length" of Long, parameter "max_intron_length" of
           Long, parameter "no_spliced_alignment" of type "bool" (indicates
           true or false values, false <= 0, true >=1), parameter
           "transcriptome_mapping_only" of type "bool" (indicates true or
           false values, false <= 0, true >=1), parameter "tailor_alignments"
           of String
        :returns: instance of type "Hisat2Output" (Output for hisat2.
           alignment_ref: can be either an Alignment or AlignmentSet,
           depending on inputs.) -> structure: parameter "report_name" of
           String, parameter "report_ref" of String, parameter
           "alignment_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN run_hisat2
        returnVal = {
            "report_ref": None,
            "report_name": None
        }

        # steps to cover.
        # 0. check the parameters
        param_err = check_hisat2_parameters(params, self.workspace_url)
        if len(param_err) > 0:
            for err in param_err:
                print(err)
            raise ValueError("Errors found in parameters, see logs for details.")

        hs_runner = Hisat2(self.callback_url, self.workspace_url, self.shared_folder)

        # 1. Get list of reads object references
        # sampleset_ref = params["sampleset_ref"]
        reads_refs = fetch_reads_refs_from_sampleset(
            params["sampleset_ref"], self.workspace_url, self.callback_url
        )

        # 2. Run hisat with index and reads.
        alignments = dict()
        output_ref = None

        # If there's only one, run it locally right now.
        # If there's more than one:
        #  1. make a list of tasks to send to KBParallel.
        #  2. add a flag to not make a report for each subtask.
        #  3. make the report when it's all done.
        if len(reads_refs) == 1:
            (alignments, output_ref) = hs_runner.run_single(reads_refs[0], params)
        else:
            (alignments, output_ref) = hs_runner.run_batch(reads_refs, params)

            base_output_obj_name = params["alignmentset_name"]
            # build task list and send it to KBParallel
            tasks = list()
            for idx, reads_ref in enumerate(reads_refs):
                single_param = dict(params)  # need a copy of the params
                single_param["alignmentset_name"] = "{}_{}".format(base_output_obj_name, idx)
                single_param["build_report"] = 0
                single_param["sampleset_ref"] = reads_ref["ref"]
                if "condition" in reads_ref:
                    single_param["condition"] = reads_ref["condition"]
                else:
                    single_param["condition"] = "unspecified"

                tasks.append({
                    "module_name": "kb_hisat2",
                    "function_name": "run_hisat2",
                    "version": "dev",
                    "parameters": single_param
                })
            batch_run_params = {
                "tasks": tasks,
                "runner": "parallel",
                "concurrent_local_tasks": 3,
                "concurrent_njsw_tasks": 0,
                "max_retries": 2
            }
            parallel_runner = KBParallel(self.callback_url)
            results = parallel_runner.run_batch(batch_run_params)["results"]
            alignment_items = list()
            for idx, result in enumerate(results):
                # idx of the result is the same as the idx of the inputs AND reads_refs
                if result["is_error"] != 0:
                    raise RuntimeError("Failed a parallel run of HISAT2! {}".format(result["result_package"]["error"]))
                reads_ref = tasks[idx]["parameters"]["sampleset_ref"]
                alignment_items.append({
                    "ref": result["result_package"]["result"][0]["alignment_ref"],
                    "label": reads_refs[idx].get(
                        "condition",
                        params.get("condition",
                                   "unspecified condition"))
                })
                alignments[reads_ref] = {
                    "ref": result["result_package"]["result"][0]["alignment_ref"],
                    "name": tasks[idx]["parameters"]["alignmentset_name"]
                }

            # build the final alignment set
            output_ref = hs_runner.upload_alignment_set(
                alignment_items, base_output_obj_name, params["ws_name"]
            )

        if params.get("build_report", 0) == 1:
            report_info = hs_runner.build_report(params, reads_refs, alignments)
            returnVal["report_ref"] = report_info["ref"]
            returnVal["report_name"] = report_info["name"]
        returnVal["alignment_objs"] = alignments
        returnVal["alignment_ref"] = output_ref
        if len(reads_refs) == 1:
            returnVal["alignment_name"] = params["alignmentset_name"]
        else:
            returnVal["alignment_name"] = base_output_obj_name

        #END run_hisat2

        # At some point might do deeper type checking...
        if not isinstance(returnVal, dict):
            raise ValueError('Method run_hisat2 return value ' +
                             'returnVal is not type dict as required.')
        # return the results
        return [returnVal]
    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
