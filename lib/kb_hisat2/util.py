from Workspace.WorkspaceClient import Workspace
from AssemblyUtil.AssemblyUtilClient import AssemblyUtil


def check_hisat2_parameters(params):
    """
    Checks to ensure that the hisat2 parameter set is correct and has the right
    mash of options.
    Returns a list of error strings if there's a problem, or just an empty list otherwise.
    """
    errors = list()
    return errors

def setup_hisat2():
    pass



def fetch_fasta_from_genome(genome_ref, ws_url, callback_url):
    """
    Returns an assembly or contigset as FASTA.
    """
    if not check_ref_type(genome_ref, ['KBaseGenomes.Genome'], ws_url):
        raise ValueError("The given genome_ref {} is not a KBaseGenomes.Genome type!")
    # test if genome references an assembly type
    # do get_objects2 without data. get list of refs
    ws = Workspace(ws_url)
    genome_obj_info = ws.get_objects2({
        'objects': [{'ref': genome_ref}],
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

    if len(assembly_ref) == 1:
        return fetch_fasta_from_assembly(assembly_ref, ws_url, callback_url)
    else:
        raise ValueError("Multiple assemblies found associated with the given genome ref {}! Unable to continue.")


def fetch_fasta_from_assembly(assembly_ref, ws_url, callback_url):
    """
    From an assembly or contigset, this uses a data file util to build a FASTA file and return the
    path to it.
    """
    allowed_types = ['KBaseFile.Assembly', 'KBaseAssembly.Assembly', 'KBaseGenomes.ContigSet']
    if not check_ref_type(assembly_ref, allowed_types, ws_url):
        raise ValueError("The given reference {} is invalid for fetching a FASTA file")
    au = AssemblyUtil(callback_url)
    return au.get_assembly_as_fasta({'ref': assembly_ref})


def fetch_fasta_from_object(ref, ws_url, callback_url):
    obj_type = get_object_type(ref, ws_url)
    if "KBaseGenomes.Genome" in obj_type:
        return fetch_fasta_from_genome(ref, ws_url, callback_url)
    elif "KBaseGenomeAnnotations.Assembly" in obj_type or "KBaseGenomes.ContigSet" in obj_type:
        return fetch_fasta_from_assembly(ref, ws_url, callback_url)
    else:
        raise ValueError("Unable to fetch a FASTA file from an object of type {}".format(obj_type))


def check_ref_type(ref, allowed_types, ws_url):
    obj_type = get_object_type(ref, ws_url).lower()
    for t in allowed_types:
        if t.lower() in obj_type:
            return True
    return False


def get_object_type(ref, ws_url):
    ws = Workspace(ws_url)
    info = ws.get_object_info3({'objects': [{'ref': ref}]})
    obj_info = info.get('infos', [[]])[0]
    if len(obj_info) == 0:
        raise RuntimeError("An error occurred while fetching type info from the Workspace. No information returned for reference {}".format(ref))
    return obj_info[2]
