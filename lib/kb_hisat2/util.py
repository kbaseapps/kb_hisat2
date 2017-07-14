"""
Some utility functions for the HISAT2 module.
These mainly deal with manipulating files from Workspace objects.
There's also some parameter checking and munging functions.
"""
from __future__ import print_function
import re
from pprint import pprint
from Workspace.WorkspaceClient import Workspace
from DataFileUtil.DataFileUtilClient import DataFileUtil


def check_hisat2_parameters(params, ws_url):
    """
    Checks to ensure that the hisat2 parameter set is correct and has the right
    mash of options.
    Returns a list of error strings if there's a problem, or just an empty list otherwise.
    """
    errors = list()
    # parameter keys and rules:
    # -------------------------
    # ws_name - workspace name, string, required
    # alignmentset_name - output object name, string, required
    # string sampleset_ref - input reads object ref, string, required
    # string genome_ref - input genome object ref, string, required
    # num_threads - int, >= 1, optional
    # quality_score - string, one of phred33 or phred64, optional (default phred33)
    # skip - int, >= 0, optional
    # trim3 - int, >= 0, optional
    # trim5 - int, >= 0, optional
    # np - int,
    # minins - int,
    # maxins - int,
    # orientation - string, one of fr, rr, rf, ff, optional (default fr)
    # min_intron_length, int, >= 0, required
    # int max_intron_length - int, >= 0, required
    # bool no_spliced_alignment - 0 or 1, optional (default 0)
    # bool transcriptome_mapping_only - 0 or 1, optional (default 0)
    # string tailor_alignments - string ...?
    print("Checking input parameters")
    pprint(params)
    if "ws_name" not in params or not valid_string(params["ws_name"]):
        errors.append("Parameter ws_name must be a valid workspace "
                      "name, not {}".format(params.get("ws_name", None)))
    if "alignmentset_name" not in params or not valid_string(params["alignmentset_name"]):
        errors.append("Parameter alignmentset_name must be a valid Workspace object string, "
                      "not {}".format(params.get("alignmentset_name", None)))
    if "sampleset_ref" not in params or not valid_string(params["sampleset_ref"], is_ref=True):
        errors.append("Parameter sampleset_ref must be a valid Workspace object reference, "
                      "not {}".format(params.get("sampleset_ref", None)))
    elif check_ref_type(params["sampleset_ref"], ["PairedEndLibary", "SingleEndLibrary"], ws_url):
        if "condition" not in params or not valid_string(params["condition"]):
            errors.append("Parameter condition is required for a single "
                          "PairedEndLibrary or SingleEndLibrary")
    if "genome_ref" not in params or not valid_string(params["genome_ref"], is_ref=True):
        errors.append("Parameter genome_ref must be a valid Workspace object reference, "
                      "not {}".format(params.get("genome_ref", None)))
    return errors


def valid_string(s, is_ref=False):
    is_valid = isinstance(s, basestring) and len(s.strip()) > 0
    if is_valid and is_ref:
        is_valid = check_reference(s)
    return is_valid


def check_reference(ref):
    """
    Tests the given ref string to make sure it conforms to the expected
    object reference format. Returns True if it passes, False otherwise.
    """
    obj_ref_regex = re.compile("^(?P<wsid>\d+)\/(?P<objid>\d+)(\/(?P<ver>\d+))?$")
    ref_path = ref.strip().split(";")
    for step in ref_path:
        if not obj_ref_regex.match(step):
            return False
    return True


def check_ref_type(ref, allowed_types, ws_url):
    """
    Validates the object type of ref against the list of allowed types. If it passes, this
    returns True, otherwise False.
    Really, all this does is verify that at least one of the strings in allowed_types is
    a substring of the ref object type name.
    Ex1:
    ref = "KBaseGenomes.Genome-4.0"
    allowed_types = ["assembly", "KBaseFile.Assembly"]
    returns False
    Ex2:
    ref = "KBaseGenomes.Genome-4.0"
    allowed_types = ["assembly", "genome"]
    returns True
    """
    obj_type = get_object_type(ref, ws_url).lower()
    for t in allowed_types:
        if t.lower() in obj_type:
            return True
    return False


def get_object_type(ref, ws_url):
    """
    Fetches and returns the typed object name of ref from the given workspace url.
    If that object doesn't exist, or there's another Workspace error, this raises a
    RuntimeError exception.
    """
    ws = Workspace(ws_url)
    info = ws.get_object_info3({"objects": [{"ref": ref}]})
    obj_info = info.get("infos", [[]])[0]
    if len(obj_info) == 0:
        raise RuntimeError("An error occurred while fetching type info from the Workspace. "
                           "No information returned for reference {}".format(ref))
    return obj_info[2]


def get_object_names(ref_list, ws_url):
    """
    From a list of workspace references, returns a mapping from ref -> name of the object.
    """
    ws = Workspace(ws_url)
    obj_ids = list()
    for ref in ref_list:
        obj_ids.append({"ref": ref})
    info = ws.get_object_info3({"objects": obj_ids})
    name_map = dict()
    # might be in a data palette, so we can't just use the ref.
    for i in range(len(info["infos"])):
        name_map[";".join(info["paths"][i])] = info["infos"][i][1]
    return name_map


def package_directory(callback_url, dir_path, zip_file_name, zip_file_description):
    ''' Simple utility for packaging a folder and saving to shock '''
    dfu = DataFileUtil(callback_url)
    output = dfu.file_to_shock({'file_path': dir_path,
                                'make_handle': 0,
                                'pack': 'zip'})
    return {'shock_id': output['shock_id'],
            'name': zip_file_name,
            'description': zip_file_description}
