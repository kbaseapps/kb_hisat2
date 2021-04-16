"""
Some test utility functions for uploading test data.
"""
from installed_clients.AssemblyUtilClient import AssemblyUtil
from installed_clients.GenomeFileUtilClient import GenomeFileUtil
from installed_clients.ReadsUtilsClient import ReadsUtils
from installed_clients.SetAPIServiceClient import SetAPI
from installed_clients.WorkspaceClient import Workspace
from installed_clients.DataFileUtilClient import DataFileUtil


def load_fasta_file(callback_url, ws_name, filename, obj_name, contents):
    """
    Loads the given FASTA file into a workspace as an Assembly object.
    """
    f = open(filename, 'w')
    f.write(contents)
    f.close()
    assembly_util = AssemblyUtil(callback_url)
    assembly_ref = assembly_util.save_assembly_from_fasta({
        'file': {'path': filename},
        'workspace_name': ws_name,
        'assembly_name': obj_name
    })
    return assembly_ref


def load_genbank_file(callback_url, ws_name, local_file, target_name):
    """
    Loads a Genbank (.gbk/.gbff/etc.) file into a workspace as a Genome object. This
    has the side effect of building an Assembly to contain the genome sequence.
    """
    gfu = GenomeFileUtil(callback_url)
    genome_ref = gfu.genbank_to_genome({
        "file": {
            "path": local_file
        },
        "genome_name": target_name,
        "workspace_name": ws_name,
        "source": "Ensembl",
        "type": "User upload",
        "generate_ids_if_needed": 1
    })
    return genome_ref.get('genome_ref')  # yeah, i know.


def load_reads(callback_url, ws_name, tech, file_fwd, file_rev, target_name):
    """
    Loads FASTQ files as either SingleEndLibrary or PairedEndLibrary. If file_rev is None,
    then we get a single end, otherwise, paired.
    """
    reads_util = ReadsUtils(callback_url)
    upload_params = {
        "wsname": ws_name,
        "fwd_file": file_fwd,
        "name": target_name,
        "sequencing_tech": tech
    }
    if file_rev is not None:
        upload_params["rev_file"] = file_rev
    reads_ref = reads_util.upload_reads(upload_params)
    return reads_ref["obj_ref"]


def load_reads_set(srv_wiz_url, ws_name, reads_set, target_name):
    """
    Combine a list of reads references into a ReadsSet.
    if file_rev is None or not a present key, then this is treated as a single end reads.
    """
    set_client = SetAPI(srv_wiz_url)
    set_output = set_client.save_reads_set_v1({
        "workspace": ws_name,
        "output_object_name": target_name,
        "data": {
            "description": "reads set for testing",
            "items": reads_set
        }
    })
    return set_output["set_ref"]


def load_sample_set(workspace_url, ws_name, reads_refs, conditions, library_type, target_name):
    """
    Upload a set of files as a sample set.
    library_type = "SingleEnd" or "PairedEnd"
    """
    sample_set = {
        "Library_type": library_type,
        "domain": "Prokaryotes",
        "num_samples": len(reads_refs),
        "platform": None,
        "publication_id": None,
        "sample_ids": reads_refs,
        "sampleset_desc": None,
        "sampleset_id": target_name,
        "condition": conditions,
        "source": None
    }
    ws_client = Workspace(workspace_url)
    ss_obj = ws_client.save_objects({
        "workspace": ws_name,
        "objects": [{
            "type": "KBaseRNASeq.RNASeqSampleSet",
            "data": sample_set,
            "name": target_name,
            "provenance": [{"input_ws_objects": reads_refs}]
        }]
    })
    ss_ref = "{}/{}/{}".format(ss_obj[0][6], ss_obj[0][0], ss_obj[0][4])
    return ss_ref


def load_ama(workspace_url, callback_url, ws_name, assembly_ref, local_file, target_name):
    """
    Upload a mini test AnnotatedMetagenomeAssembly object
    """
    dfu = DataFileUtil(callback_url)
    handle_ref = dfu.file_to_shock({'file_path': local_file,
                                    'make_handle': True})['handle']['hid']

    ama_data = {
        "feature_counts": {'test_feature': 10},
        "dna_size": 10,
        "num_contigs": 10,
        "num_features": 10,
        "molecule_type": 'test molecule type',
        "source": 'User_upload',
        "md5": 'test md5',
        "gc_content": 0.1,
        "assembly_ref": assembly_ref,
        "features_handle_ref": handle_ref,
        "protein_handle_ref": handle_ref,
        "environment": 'test environment'
    }
    ws_client = Workspace(workspace_url)
    ss_obj = ws_client.save_objects({
        "workspace": ws_name,
        "objects": [{
            "type": "KBaseMetagenomes.AnnotatedMetagenomeAssembly",
            "data": ama_data,
            "name": target_name
        }]
    })
    ss_ref = "{}/{}/{}".format(ss_obj[0][6], ss_obj[0][0], ss_obj[0][4])
    return ss_ref
