/*
A KBase module: kb_hisat2
*/

module kb_hisat2 {
/* indicates true or false values, false <= 0, true >=1 */
    typedef int bool;

/*
     Object for Report type
*/
    typedef structure {
		string report_name;
		string report_ref;
    } ResultsToReport;


/*
Input for hisat2.
ws_name = the workspace name provided by the narrative for storing output.
sampleset_ref = the workspace reference for the sampleset of reads to align.
genome_ref = the workspace reference for the reference genome that HISAT2 will align against.
alignmentset_name = the name of the alignment set object to create.
num_threads = the number of threads to tell hisat to use (NOT USER SET?)
quality_score = one of phred33 or phred64
skip =
trim3 =
trim5 =
np =
minins =
maxins =
orientation =
min_intron_length =
max_intron_length =
no_spliced_alignment =
transcriptome_mapping_only =
tailor_alignments =
condition = a string stating the experimental condition of the reads. REQUIRED for single reads,
            ignored for sets.
*/
    typedef structure {
        string ws_name;
        string alignmentset_name;
        string sampleset_ref;
        string condition;
        string genome_ref;
        int num_threads;
        string quality_score;
        int skip;
        int trim3;
        int trim5;
        int np;
        int minins;
        int maxins;
        string orientation;
        int min_intron_length;
        int max_intron_length;
        bool no_spliced_alignment;
        bool transcriptome_mapping_only;
        string tailor_alignments;
    } Hisat2Params;

    funcdef run_hisat2(Hisat2Params params)
        returns(ResultsToReport) authentication required;
};
