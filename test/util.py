"""
Some test utility functions for uploading test data.
"""
from GenomeFileUtil.GenomeFileUtilClient import GenomeFileUtil
from ReadsUtils.ReadsUtilsClient import ReadsUtils
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil
from SetAPI.SetAPIClient import SetAPI


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
        "source": "RefSeq",
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


def load_reads_set(callback_url, ws_name, local_files, target_name):
    """
    Upload a set of reads as a ReadsSet.
    each file in local_files is a structure:
    {
        file_fwd = path_to_file,
        file_rev = path_to_reverse_file,
        tech = sequencing tech,
        target_name = name of uploaded reads object
    }
    if file_rev is None or not a present key, then this is treated as a single end reads.
    """
    reads_set = list()
    for reads in local_files:
        reads_set.append({
            "ref": load_reads(callback_url, ws_name, reads["tech"], reads["file_fwd"],
                              reads.get("file_rev", None), reads["target_name"]),
            "label": "a_reads_object"
        })
    set_client = SetAPI(callback_url)
    set_output = set_client.save_reads_set_v1({
        "workspace": ws_name,
        "output_object_name": target_name,
        "data": {
            "description": "reads set for testing",
            "items": reads_set
        }
    })
    return set_output["set_ref"]


def load_sample_set(self, local_files, target_name):
    """
    Upload a set of files as a sample set.
    """
    return None
