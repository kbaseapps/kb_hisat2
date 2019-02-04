import os  # noqa: F401
import shutil
import time
import unittest
from configparser import ConfigParser  # py3
from os import environ

from installed_clients.DataFileUtilClient import DataFileUtil
from installed_clients.WorkspaceClient import Workspace
from kb_hisat2.authclient import KBaseAuth as _KBaseAuth
from kb_hisat2.hisat2indexmanager import Hisat2IndexManager
from kb_hisat2.kb_hisat2Impl import kb_hisat2
from kb_hisat2.kb_hisat2Server import MethodContext
from kb_hisat2.util import check_reference, get_object_names
from util import (
    load_genbank_file,
    load_reads,
    load_reads_set,
    load_sample_set,
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
        cls.ws_client = Workspace(cls.wsURL)
        cls.serviceImpl = kb_hisat2(cls.cfg)
        cls.scratch = cls.cfg['scratch']
        cls.callback_url = os.environ['SDK_CALLBACK_URL']
        cls.srv_wiz_url = cls.cfg['srv-wiz-url']

        # set up the test workspace
        cls.ws_name = "test_kb_hisat2_{}".format(int(time.time() * 1000))
        cls.ws_client.create_workspace({"workspace": cls.ws_name})

        cls.dfu = DataFileUtil(cls.callback_url)

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
            "label": "rs_wt1"
        }, {
            "ref": cls.single_end_ref_wt_2,
            "label": "rs_wt2"
        }]
        cls.single_end_reads_set = load_reads_set(
            cls.srv_wiz_url, cls.ws_name, reads_set, "se_reads_set"
        )

        # Upload test SampleSet of single end reads
        cls.reads_refs = [
            cls.single_end_ref_wt_1,
            cls.single_end_ref_wt_2
        ]
        conditions = [
            "ss_wt1",
            "ss_wt2"
        ]
        cls.single_end_sampleset = load_sample_set(
            cls.wsURL, cls.ws_name, cls.reads_refs, conditions, "SingleEnd", "se_sampleset"
        )
        genome_obj_info = cls.ws_client.get_objects2({
            'objects': [{'ref': cls.genome_ref}],
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
        ref_info = cls.ws_client.get_object_info3({'objects': ref_params})
        for idx, info in enumerate(ref_info.get('infos')):
            if "KBaseGenomeAnnotations.Assembly" in info[2] or "KBaseGenomes.ContigSet" in info[2]:
                assembly_ref.append(";".join(ref_info.get('paths')[idx]))
        cls.assembly_ref = assembly_ref[0]

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
        idx_prefix = manager.get_hisat2_index(self.assembly_ref)
        self.assertIn("kb_hisat2_idx", idx_prefix)

    def test_run_hisat2_readsset_ok(self):
        res = self.get_impl().run_hisat2(self.get_context(), {
            "ws_name": self.ws_name,
            "sampleset_ref": self.single_end_reads_set,
            "genome_ref": self.genome_ref,
            "alignmentset_suffix": "_alignment_set",
            "alignment_suffix": "_alignment",
            "num_threads": 2,
            "quality_score": "phred33",
            "skip": 0,
            "trim3": 0,
            "trim5": 0,
            "np": 1,
            "min_intron_length": 20,
            "max_intron_length": 500000,
            "no_spliced_alignment": 0,
            "build_report": 1
        })[0]
        self.assertIsNotNone(res)
        print("Done with HISAT2 run! {}".format(res))
        self.assertIn("report_ref", res)
        self.assertTrue(check_reference(res["report_ref"]))
        self.assertIn("report_name", res)
        self.assertIn("alignmentset_ref", res)
        self.assertTrue(check_reference(res["alignmentset_ref"]))
        self.assertTrue(get_object_names([res["alignmentset_ref"]], self.wsURL)[res["alignmentset_ref"]].endswith("_alignment_set"))
        self.assertIn("alignment_objs", res)
        self.assertTrue(len(list(res["alignment_objs"].keys())) == 2)
        for reads_ref in res["alignment_objs"]:
            ref_from_refpath = reads_ref.split(';')[-1]
            self.assertIn(ref_from_refpath, self.reads_refs)
            self.assertTrue(res["alignment_objs"][reads_ref]["name"].endswith("_alignment"))
            self.assertTrue(check_reference(res["alignment_objs"][reads_ref]["ref"]))

    def test_run_hisat2_single_end_lib_ok(self):
        res = self.get_impl().run_hisat2(self.get_context(), {
            "ws_name": self.ws_name,
            "sampleset_ref": self.single_end_ref_wt_1,
            "condition": "wt",
            "genome_ref": self.genome_ref,
            "alignmentset_suffix": "_alignment_set",
            "alignment_suffix": "_alignment",
            "num_threads": 2,
            "quality_score": "phred33",
            "skip": 0,
            "trim3": 0,
            "trim5": 0,
            "np": 1,
            "min_intron_length": 20,
            "max_intron_length": 500000,
            "no_spliced_alignment": 0,
            "build_report": 1
        })[0]
        self.assertIsNotNone(res)
        print("Done with HISAT2 run! {}".format(res))
        self.assertIn("report_ref", res)
        self.assertTrue(check_reference(res["report_ref"]))
        self.assertIn("report_name", res)
        self.assertIn("alignmentset_ref", res)
        self.assertIsNone(res["alignmentset_ref"])
        self.assertIn("alignment_objs", res)
        self.assertTrue(len(res["alignment_objs"].keys()) == 1)
        for reads_ref in res["alignment_objs"]:
            ref_from_refpath = reads_ref.split(';')[-1]
            self.assertIn(ref_from_refpath, self.reads_refs)
            self.assertTrue(res["alignment_objs"][reads_ref]["name"].endswith("_alignment"))
            alignment_ref = res["alignment_objs"][reads_ref]["ref"]
            self.assertTrue(check_reference(alignment_ref))
            alignment_data = self.dfu.get_objects(
                                {"object_refs": [alignment_ref]})['data'][0]['data']
            align_stats = alignment_data.get('alignment_stats')
            self.assertEqual(align_stats.get('total_reads'), 15254)
            self.assertEqual(align_stats.get('mapped_reads'), 15081)
            self.assertEqual(align_stats.get('unmapped_reads'), 173)
            self.assertEqual(align_stats.get('singletons'), 11044)
            self.assertEqual(align_stats.get('multiple_alignments'), 4037)

    def test_run_hisat2_assembly_ok(self):
        res = self.get_impl().run_hisat2(self.get_context(), {
            "ws_name": self.ws_name,
            "sampleset_ref": self.single_end_ref_wt_1,
            "condition": "wt",
            "genome_ref": self.assembly_ref,
            "alignmentset_suffix": "_alignment_set",
            "alignment_suffix": "_alignment",
            "num_threads": 2,
            "quality_score": "phred33",
            "skip": 0,
            "trim3": 0,
            "trim5": 0,
            "np": 1,
            "min_intron_length": 20,
            "max_intron_length": 500000,
            "no_spliced_alignment": 0,
            "transcriptome_mapping_only": 0,
            "build_report": 1
        })[0]
        self.assertIsNotNone(res)
        print("Done with HISAT2 run! {}".format(res))
        self.assertIn("report_ref", res)
        self.assertTrue(check_reference(res["report_ref"]))
        self.assertIn("report_name", res)
        self.assertIn("alignmentset_ref", res)
        self.assertIsNone(res["alignmentset_ref"])
        self.assertIn("alignment_objs", res)
        self.assertTrue(len(res["alignment_objs"].keys()) == 1)
        for reads_ref in res["alignment_objs"]:
            ref_from_refpath = reads_ref.split(';')[-1]
            self.assertIn(ref_from_refpath, self.reads_refs)
            self.assertTrue(res["alignment_objs"][reads_ref]["name"].endswith("_alignment"))
            self.assertTrue(check_reference(res["alignment_objs"][reads_ref]["ref"]))

    def test_run_hisat2_sampleset_ok(self):
        res = self.get_impl().run_hisat2(self.get_context(), {
            "ws_name": self.ws_name,
            "sampleset_ref": self.single_end_sampleset,
            "genome_ref": self.genome_ref,
            "alignmentset_suffix": "_sampleset_alignments",
            "alignment_suffix": "_sampleset_alignment",
            "num_threads": 2,
            "quality_score": "phred33",
            "skip": 0,
            "trim3": 0,
            "trim5": 0,
            "np": 1,
            "min_intron_length": 20,
            "max_intron_length": 500000,
            "no_spliced_alignment": 0,
            "build_report": 1
        })[0]
        self.assertIsNotNone(res)
        print("Done with HISAT2 run! {}".format(res))
        self.assertIn("report_ref", res)
        self.assertTrue(check_reference(res["report_ref"]))
        self.assertIn("report_name", res)
        self.assertIn("alignmentset_ref", res)
        self.assertTrue(check_reference(res["alignmentset_ref"]))
        self.assertTrue(get_object_names([res["alignmentset_ref"]], self.wsURL)[res["alignmentset_ref"]].endswith("_sampleset_alignments"))
        self.assertIn("alignment_objs", res)
        self.assertTrue(len(res["alignment_objs"].keys()) == 2)
        for reads_ref in res["alignment_objs"]:
            ref_from_refpath = reads_ref.split(';')[-1]
            self.assertIn(ref_from_refpath, self.reads_refs)
            self.assertTrue(res["alignment_objs"][reads_ref]["name"].endswith("_sampleset_alignment"))
            self.assertTrue(check_reference(res["alignment_objs"][reads_ref]["ref"]))

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

    def test_status(self):
        res = self.get_impl().status(self.get_context())
        self.assertIsNotNone(res)
        self.assertTrue(res[0]['state'] == 'OK')
