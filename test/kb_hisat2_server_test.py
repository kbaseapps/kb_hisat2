# -*- coding: utf-8 -*-
from __future__ import print_function
import unittest
import os  # noqa: F401
import json  # noqa: F401
import time
import requests
import shutil

from os import environ
try:
    from ConfigParser import ConfigParser  # py2
except:
    from configparser import ConfigParser  # py3

from pprint import pprint  # noqa: F401

from biokbase.workspace.client import Workspace as workspaceService
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
from kb_hisat2.kb_hisat2Impl import kb_hisat2
from kb_hisat2.kb_hisat2Server import MethodContext
from kb_hisat2.authclient import KBaseAuth as _KBaseAuth
from kb_hisat2.hisat2indexmanager import Hisat2IndexManager

from AssemblyUtil.AssemblyUtilClient import AssemblyUtil


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
        cls.wsClient = workspaceService(cls.wsURL)
        cls.serviceImpl = kb_hisat2(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'wsName'):
            cls.wsClient.delete_workspace({'workspace': cls.wsName})
            print('Test workspace was deleted')

    def get_ws_client(self):
        return self.__class__.wsClient

    def get_ws_name(self):
        if hasattr(self.__class__, 'wsName'):
            return self.__class__.wsName
        suffix = int(time.time() * 1000)
        wsName = "test_kb_hisat2_" + str(suffix)
        ret = self.get_ws_client().create_workspace({'workspace': wsName})  # noqa
        self.__class__.wsName = wsName
        return wsName

    def get_impl(self):
        return self.__class__.serviceImpl

    def get_context(self):
        return self.__class__.ctx

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    def load_fasta_file(self, filename, obj_name, contents):
        f = open(filename, 'w')
        f.write(contents)
        f.close()
        assembly_util = AssemblyUtil(self.callback_url)
        assembly_ref = assembly_util.save_assembly_from_fasta({
            'file': {'path': filename},
            'workspace_name': self.get_ws_name(),
            'assembly_name': obj_name
        })
        return assembly_ref

    def load_genbank_file(self, local_file, target_name):
        gfu = GenomeFileUtil(self.callback_url)
        genome_ref = gfu.genbank_to_genome({
            "file": {
                "path": local_file
            },
            "genome_name": target_name,
            "workspace_name": self.get_ws_name(),
            "source": "RefSeq",
            "genetic_code": 11,
            "type": "User upload"
        })
        return genome_ref.get('genome_ref') # yeah, i know.

    def load_reads(self, local_file, target_name):
        pass

    def load_reads_set(self, local_files, target_name):
        pass

    def load_sample_set(self, local_files, target_name):
        pass

    def test_build_hisat2_index_from_genome_ok(self):
        base_gbk_file = "data/streptococcus_pneumoniae_R6_ref.gbff"
        gbk_file = os.path.join(self.scratch, os.path.basename(base_gbk_file))
        shutil.copy(base_gbk_file, gbk_file)
        genome_ref = self.load_genbank_file(gbk_file, 'my_test_genome')
        manager = Hisat2IndexManager(self.wsURL, self.callback_url, self.scratch)
        print("getting hisat2 index from ref = {}".format(genome_ref))
        idx_prefix = manager.get_hisat2_index(genome_ref)
        self.assertIsNotNone(idx_prefix)

    def test_build_hisat2_index_from_genome_no_assembly(self):
        pass

    def test_build_hisat2_index_bad_object(self):
        pass

    def test_build_hisat2_index_no_object(self):
        pass

    def test_build_hisat2_index_from_assembly_ok(self):
        pass

    def test_run_hisat2_readsset_ok(self):
        pass

    def test_run_hisat2_single_end_lib_ok(self):
        pass

    def test_run_hisat2_paired_end_lib_ok(self):
        pass

    def test_run_hisat2_missing_genome(self):
        pass

    def test_run_hisat2_missing_seq(self):
        pass

    def test_run_hisat2_missing_reads(self):
        pass

    def test_run_hisat2_parameter_sets(self):
        pass


    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    # def test_filter_contigs_ok(self):
    #
    #     # First load a test FASTA file as an KBase Assembly
    #     fasta_content = '>seq1 something soemthing asdf\n' \
    #                     'agcttttcat\n' \
    #                     '>seq2\n' \
    #                     'agctt\n' \
    #                     '>seq3\n' \
    #                     'agcttttcatgg'
    #
    #     assembly_ref = self.load_fasta_file(os.path.join(self.scratch, 'test1.fasta'),
    #                                         'TestAssembly',
    #                                         fasta_content)
    #
    #     # Second, call your implementation
    #     ret = self.getImpl().filter_contigs(self.getContext(),
    #                                         {'workspace_name': self.getWsName(),
    #                                          'assembly_input_ref': assembly_ref,
    #                                          'min_length': 10
    #                                          })
    #
    #     # Validate the returned data
    #     self.assertEqual(ret[0]['n_initial_contigs'], 3)
    #     self.assertEqual(ret[0]['n_contigs_removed'], 1)
    #     self.assertEqual(ret[0]['n_contigs_remaining'], 2)
    #
    # def test_filter_contigs_err1(self):
    #     with self.assertRaises(ValueError) as errorContext:
    #         self.getImpl().filter_contigs(self.getContext(),
    #                                       {'workspace_name': self.getWsName(),
    #                                        'assembly_input_ref': '1/fake/3',
    #                                        'min_length': '-10'})
    #     self.assertIn('min_length parameter cannot be negative', str(errorContext.exception))
    #
    # def test_filter_contigs_err2(self):
    #     with self.assertRaises(ValueError) as errorContext:
    #         self.getImpl().filter_contigs(self.getContext(),
    #                                       {'workspace_name': self.getWsName(),
    #                                        'assembly_input_ref': '1/fake/3',
    #                                        'min_length': 'ten'})
    #     self.assertIn('Cannot parse integer from min_length parameter', str(errorContext.exception))
