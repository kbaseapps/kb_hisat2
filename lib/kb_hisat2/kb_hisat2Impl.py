# -*- coding: utf-8 -*-
#BEGIN_HEADER
# The header block is where all import statments should live
from __future__ import print_function
import os
from Bio import SeqIO
from pprint import pprint, pformat
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from KBaseReport.KBaseReportClient import KBaseReport
from util import (
    check_hisat2_parameters,
    setup_hisat2
)
#END_HEADER


class kb_hisat2:
    '''
    Module Name:
    kb_hisat2

    Module Description:
    A KBase module: kb_hisat2
This sample module contains one small method - filter_contigs.
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = "https://github.com/briehl/kb_hisat2"
    GIT_COMMIT_HASH = "2d7e32ccd12fa157beba745dee22afbeb9eec74d"

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
        self.shared_folder = config['scratch']
        self.num_threads = 2

        #END_CONSTRUCTOR


    def run_hisat2(self, ctx, params):
        """
        :param params: instance of type "Hisat2Params" -> structure:
           parameter "ws_id" of String, parameter "sampleset_id" of String,
           parameter "genome_id" of String, parameter "num_threads" of Long,
           parameter "quality_score" of String, parameter "skip" of Long,
           parameter "trim3" of Long, parameter "trim5" of Long, parameter
           "np" of Long, parameter "minins" of Long, parameter "maxins" of
           Long, parameter "orientation" of String, parameter
           "min_intron_length" of Long, parameter "max_intron_length" of
           Long, parameter "no_spliced_alignment" of type "bool" (indicates
           true or false values, false <= 0, true >=1), parameter
           "transcriptome_mapping_only" of type "bool" (indicates true or
           false values, false <= 0, true >=1), parameter "tailor_alignments"
           of String
        :returns: instance of type "ResultsToReport" (Object for Report type)
           -> structure: parameter "report_name" of String, parameter
           "report_ref" of String
        """
        # ctx is the context object
        # return variables are: returnVal
        #BEGIN run_hisat2

        # steps to cover.
        # 0. check the parameters
        param_err = check_hisat2_parameters(params)
        if len(param_err) > 0:
            for err in param_err:
                print(err)
            raise ValueError("Errors found in parameters, see above for details.")

        hs_runner = Hisat2()
        # 1. Get hisat2 index from genome.
        #    a. If it exists in cache, use that.
        #    b. Otherwise, build it (TODO: make get_hisat2_index function)
        index_info = hs_runner.build_index()
        # 2. Get reads as files in filesystem (DFU function)

        # 3. Run hisat with index and reads.
        return_val = hs_runner.run_hisat2()

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
