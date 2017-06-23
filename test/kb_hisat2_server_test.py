# -*- coding: utf-8 -*-
from __future__ import print_function
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from kb_hisat2.kb_hisat2Impl import kb_hisat2
from kb_hisat2.kb_hisat2Server import MethodContext
from kb_hisat2.authclient import KBaseAuth as _KBaseAuth
from kb_hisat2.hisat2indexmanager import Hisat2IndexManager
from Workspace.WorkspaceClient import Workspace
from util import (
    load_genbank_file,
    load_reads,
    load_reads_set,
    load_sample_set
)

TEST_GBK_FILE = os.path.join("data", "at_chrom1_section.gbk")
TEST_READS_WT_1_FILE = os.path.join("data", "extracted_WT_rep1.fastq")
TEST_READS_WT_2_FILE = os.path.join("data", "extracted_WT_rep2.fastq")
TEST_READS_HY5_1_FILE = os.path.join("data", "extracted_hy5_rep1.fastq")
TEST_READS_HY5_2_FILE = os.path.join("data", "extracted_hy5_rep2.fastq")


class kb_hisat2Test(unittest.TestCase):
    """
    TestCase class for the kb_hisat2 module.
    """
    @classmethod
    def setUpClass(cls):
        token = environ.get('KB_AUTH_TOKEN', None)
        config_file = environ.get('KB_DEPLOYMENT_CONFIG', None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items('kb_hisat2'):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        auth_url = cls.cfg['auth-service-url']
        auth_client = _KBaseAuth(auth_url)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update({'token': token,
                        'user_id': user_id,
                        'provenance': [{
                            'service': 'kb_hisat2',
                            'method': 'please_never_use_it_in_production',
                            'method_params': []
                        }],
                        'authenticated': 1})
        cls.wsURL = cls.cfg['workspace-url']
        cls.ws_client = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_hisat2(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

        # set up the test workspace
        cls.ws_name = "test_kb_hisat2_{}".format(int(time.time() * 1000))
        cls.ws_client.create_workspace({"workspace": cls.ws_name})

        # Upload test genome
        gbk_file = os.path.join(cls.scratch, os.path.basename(TEST_GBK_FILE))
        shutil.copy(TEST_GBK_FILE, gbk_file)
        cls.genome_ref = load_genbank_file(
            cls.callback_url, cls.ws_name, gbk_file, "my_test_genome"
        )
        # Upload test reads - SingleEnd
        reads_file = os.path.join(cls.scratch, os.path.basename(TEST_READS_WT_1_FILE))
        shutil.copy(TEST_READS_WT_1_FILE, reads_file)
        cls.single_end_ref_wt_1 = load_reads(
            cls.callback_url, cls.ws_name, "Illumina", reads_file, None, "reads_wt_1"
        )
        reads_file = os.path.join(cls.scratch, os.path.basename(TEST_READS_WT_2_FILE))
        shutil.copy(TEST_READS_WT_2_FILE, reads_file)
        cls.single_end_ref_wt_2 = load_reads(
            cls.callback_url, cls.ws_name, "Illumina", reads_file, None, "reads_wt_2"
        )
        # reads_file = os.path.join(cls.scratch, os.path.basename(TEST_READS_HY5_1_FILE))
        # shutil.copy(TEST_READS_HY5_1_FILE, reads_file)
        # cls.single_end_ref_hy5_1 = load_reads(
        #     cls.callback_url, cls.ws_name, "Illumina", reads_file, None, "reads_hy5_1"
        # )
        # reads_file = os.path.join(cls.scratch, os.path.basename(TEST_READS_HY5_2_FILE))
        # shutil.copy(TEST_READS_HY5_2_FILE, reads_file)
        # cls.single_end_ref_hy5_2 = load_reads(
        #     cls.callback_url, cls.ws_name, "Illumina", reads_file, None, "reads_hy5_2"
        # )
        # Upload test reads - PairedEnd

        # Upload test ReadsSet of single end reads
        reads_set = [{
            "ref": cls.single_end_ref_wt_1,
            "label": "wt"
        }, {
            "ref": cls.single_end_ref_wt_2,
            "label": "wt"
        }]
        cls.single_end_reads_set = load_reads_set(
            cls.callback_url, cls.ws_name, reads_set, "se_reads_set"
        )

        # Upload test SampleSet of single end reads
        reads_refs = [
            cls.single_end_ref_wt_1,
            cls.single_end_ref_wt_2
        ]
        conditions = [
            "wt",
            "wt"
        ]
        cls.single_end_sampleset = load_sample_set(
            cls.wsURL, cls.ws_name, reads_refs, conditions, "SingleEnd", "se_sampleset"
        )

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'ws_name'):
            cls.ws_client.delete_workspace({'workspace': cls.ws_name})
            print('Test workspace was deleted')

    def get_ws_client(self):
        return self.__class__.ws_client

    def get_ws_name(self):
        return self.__class__.ws_name

    def get_impl(self):
        return self.__class__.serviceImpl

    def get_context(self):
        return self.__class__.ctx

    def test_build_hisat2_index_from_genome_ok(self):
        manager = Hisat2IndexManager(self.wsURL, self.callback_url, self.scratch)
        idx_prefix = manager.get_hisat2_index(self.genome_ref)
        self.assertIn("kb_hisat2_idx", idx_prefix)

    def test_build_hisat2_index_from_genome_no_assembly(self):
        pass

    def test_build_hisat2_index_bad_object(self):
        manager = Hisat2IndexManager(self.wsURL, self.callback_url, self.scratch)
        with self.assertRaises(ValueError) as err:
            manager.get_hisat2_index(self.single_end_ref_wt_1)
            self.assertIn("Incorrect object type", err.exception)

    def test_build_hisat2_index_no_object(self):
        manager = Hisat2IndexManager(self.wsURL, self.callback_url, self.scratch)
        with self.assertRaises(ValueError) as err:
            manager.get_hisat2_index(self.single_end_ref_wt_1)
            self.assertIn("Missing reference object", err.exception)

    def test_build_hisat2_index_from_assembly_ok(self):
        manager = Hisat2IndexManager(self.wsURL, self.callback_url, self.scratch)
        ws = Workspace(self.wsURL)
        genome_obj_info = ws.get_objects2({
            'objects': [{'ref': self.genome_ref}],
            'no_data': 1
        })
        # get the list of genome refs from the returned info.
        # if there are no refs (or something funky with the return), this will be an empty list.
        # this WILL fail if data is an empty list. But it shouldn't be, and we know because
        # we have a real genome reference, or get_objects2 would fail.
        genome_obj_refs = genome_obj_info.get('data', [{}])[0].get('refs', [])

        # see which of those are of an appropriate type (ContigSet or Assembly), if any.
        assembly_ref = list()
        ref_params = [{'ref': x} for x in genome_obj_refs]
        ref_info = ws.get_object_info3({'objects': ref_params})
        for idx, info in enumerate(ref_info.get('infos')):
            if "KBaseGenomeAnnotations.Assembly" in info[2] or "KBaseGenomes.ContigSet" in info[2]:
                assembly_ref.append(";".join(ref_info.get('paths')[idx]))
        assembly_ref = assembly_ref[0]
        idx_prefix = manager.get_hisat2_index(assembly_ref)
        self.assertIn("kb_hisat2_idx", idx_prefix)

    def test_run_hisat2_readsset_ok(self):
        res = self.get_impl().run_hisat2(self.get_context(), {
            "ws_name": self.ws_name,
            "sampleset_ref": self.single_end_reads_set,
            "genome_ref": self.genome_ref,
            "alignmentset_name": "new_alignment_set",
            "num_threads": 2,
            "quality_score": "phred33",
            "skip": 0,
            "trim3": 0,
            "trim5": 0,
            "np": 1,
            "min_intron_length": 20,
            "max_intron_length": 500000,
            "no_spliced_alignment": 0,
            "transcriptome_mapping_only": 0
        })
        self.assertIsNotNone(res)
        print("Done with HISAT2 run! {}".format(res))

    def test_run_hisat2_single_end_lib_ok(self):
        res = self.get_impl().run_hisat2(self.get_context(), {
            "ws_name": self.ws_name,
            "sampleset_ref": self.single_end_ref_wt_1,
            "condition": "wt",
            "genome_ref": self.genome_ref,
            "alignmentset_name": "new_alignment_set",
            "num_threads": 2,
            "quality_score": "phred33",
            "skip": 0,
            "trim3": 0,
            "trim5": 0,
            "np": 1,
            "min_intron_length": 20,
            "max_intron_length": 500000,
            "no_spliced_alignment": 0,
            "transcriptome_mapping_only": 0
        })
        self.assertIsNotNone(res)
        print("Done with HISAT2 run! {}".format(res))

    def test_run_hisat2_sampleset_ok(self):
        res = self.get_impl().run_hisat2(self.get_context(), {
            "ws_name": self.ws_name,
            "sampleset_ref": self.single_end_sampleset,
            "genome_ref": self.genome_ref,
            "alignmentset_name": "test_sampleset_alignments",
            "num_threads": 2,
            "quality_score": "phred33",
            "skip": 0,
            "trim3": 0,
            "trim5": 0,
            "np": 1,
            "min_intron_length": 20,
            "max_intron_length": 500000,
            "no_spliced_alignment": 0,
            "transcriptome_mapping_only": 0
        })
        self.assertIsNotNone(res)
        print("Done with HISAT2 run! {}".format(res))

    def test_run_hisat2_paired_end_lib_ok(self):
        pass

    def test_run_hisat2_missing_genome(self):
        pass

    def test_run_hisat2_missing_seq(self):
        pass

    def test_run_hisat2_missing_reads(self):
        pass

    def test_build_report(self):
        pass

    def test_build_report_fail(self):
        pass
