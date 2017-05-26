
package us.kbase.kbhisat2;

import java.util.HashMap;
import java.util.Map;
import javax.annotation.Generated;
import com.fasterxml.jackson.annotation.JsonAnyGetter;
import com.fasterxml.jackson.annotation.JsonAnySetter;
import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonPropertyOrder;


/**
 * <p>Original spec-file type: Hisat2Params</p>
 * 
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "ws_id",
    "sampleset_id",
    "genome_id",
    "num_threads",
    "quality_score",
    "skip",
    "trim3",
    "trim5",
    "np",
    "minins",
    "maxins",
    "orientation",
    "min_intron_length",
    "max_intron_length",
    "no_spliced_alignment",
    "transcriptome_mapping_only",
    "tailor_alignments"
})
public class Hisat2Params {

    @JsonProperty("ws_id")
    private String wsId;
    @JsonProperty("sampleset_id")
    private String samplesetId;
    @JsonProperty("genome_id")
    private String genomeId;
    @JsonProperty("num_threads")
    private Long numThreads;
    @JsonProperty("quality_score")
    private String qualityScore;
    @JsonProperty("skip")
    private Long skip;
    @JsonProperty("trim3")
    private Long trim3;
    @JsonProperty("trim5")
    private Long trim5;
    @JsonProperty("np")
    private Long np;
    @JsonProperty("minins")
    private Long minins;
    @JsonProperty("maxins")
    private Long maxins;
    @JsonProperty("orientation")
    private String orientation;
    @JsonProperty("min_intron_length")
    private Long minIntronLength;
    @JsonProperty("max_intron_length")
    private Long maxIntronLength;
    @JsonProperty("no_spliced_alignment")
    private Long noSplicedAlignment;
    @JsonProperty("transcriptome_mapping_only")
    private Long transcriptomeMappingOnly;
    @JsonProperty("tailor_alignments")
    private String tailorAlignments;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("ws_id")
    public String getWsId() {
        return wsId;
    }

    @JsonProperty("ws_id")
    public void setWsId(String wsId) {
        this.wsId = wsId;
    }

    public Hisat2Params withWsId(String wsId) {
        this.wsId = wsId;
        return this;
    }

    @JsonProperty("sampleset_id")
    public String getSamplesetId() {
        return samplesetId;
    }

    @JsonProperty("sampleset_id")
    public void setSamplesetId(String samplesetId) {
        this.samplesetId = samplesetId;
    }

    public Hisat2Params withSamplesetId(String samplesetId) {
        this.samplesetId = samplesetId;
        return this;
    }

    @JsonProperty("genome_id")
    public String getGenomeId() {
        return genomeId;
    }

    @JsonProperty("genome_id")
    public void setGenomeId(String genomeId) {
        this.genomeId = genomeId;
    }

    public Hisat2Params withGenomeId(String genomeId) {
        this.genomeId = genomeId;
        return this;
    }

    @JsonProperty("num_threads")
    public Long getNumThreads() {
        return numThreads;
    }

    @JsonProperty("num_threads")
    public void setNumThreads(Long numThreads) {
        this.numThreads = numThreads;
    }

    public Hisat2Params withNumThreads(Long numThreads) {
        this.numThreads = numThreads;
        return this;
    }

    @JsonProperty("quality_score")
    public String getQualityScore() {
        return qualityScore;
    }

    @JsonProperty("quality_score")
    public void setQualityScore(String qualityScore) {
        this.qualityScore = qualityScore;
    }

    public Hisat2Params withQualityScore(String qualityScore) {
        this.qualityScore = qualityScore;
        return this;
    }

    @JsonProperty("skip")
    public Long getSkip() {
        return skip;
    }

    @JsonProperty("skip")
    public void setSkip(Long skip) {
        this.skip = skip;
    }

    public Hisat2Params withSkip(Long skip) {
        this.skip = skip;
        return this;
    }

    @JsonProperty("trim3")
    public Long getTrim3() {
        return trim3;
    }

    @JsonProperty("trim3")
    public void setTrim3(Long trim3) {
        this.trim3 = trim3;
    }

    public Hisat2Params withTrim3(Long trim3) {
        this.trim3 = trim3;
        return this;
    }

    @JsonProperty("trim5")
    public Long getTrim5() {
        return trim5;
    }

    @JsonProperty("trim5")
    public void setTrim5(Long trim5) {
        this.trim5 = trim5;
    }

    public Hisat2Params withTrim5(Long trim5) {
        this.trim5 = trim5;
        return this;
    }

    @JsonProperty("np")
    public Long getNp() {
        return np;
    }

    @JsonProperty("np")
    public void setNp(Long np) {
        this.np = np;
    }

    public Hisat2Params withNp(Long np) {
        this.np = np;
        return this;
    }

    @JsonProperty("minins")
    public Long getMinins() {
        return minins;
    }

    @JsonProperty("minins")
    public void setMinins(Long minins) {
        this.minins = minins;
    }

    public Hisat2Params withMinins(Long minins) {
        this.minins = minins;
        return this;
    }

    @JsonProperty("maxins")
    public Long getMaxins() {
        return maxins;
    }

    @JsonProperty("maxins")
    public void setMaxins(Long maxins) {
        this.maxins = maxins;
    }

    public Hisat2Params withMaxins(Long maxins) {
        this.maxins = maxins;
        return this;
    }

    @JsonProperty("orientation")
    public String getOrientation() {
        return orientation;
    }

    @JsonProperty("orientation")
    public void setOrientation(String orientation) {
        this.orientation = orientation;
    }

    public Hisat2Params withOrientation(String orientation) {
        this.orientation = orientation;
        return this;
    }

    @JsonProperty("min_intron_length")
    public Long getMinIntronLength() {
        return minIntronLength;
    }

    @JsonProperty("min_intron_length")
    public void setMinIntronLength(Long minIntronLength) {
        this.minIntronLength = minIntronLength;
    }

    public Hisat2Params withMinIntronLength(Long minIntronLength) {
        this.minIntronLength = minIntronLength;
        return this;
    }

    @JsonProperty("max_intron_length")
    public Long getMaxIntronLength() {
        return maxIntronLength;
    }

    @JsonProperty("max_intron_length")
    public void setMaxIntronLength(Long maxIntronLength) {
        this.maxIntronLength = maxIntronLength;
    }

    public Hisat2Params withMaxIntronLength(Long maxIntronLength) {
        this.maxIntronLength = maxIntronLength;
        return this;
    }

    @JsonProperty("no_spliced_alignment")
    public Long getNoSplicedAlignment() {
        return noSplicedAlignment;
    }

    @JsonProperty("no_spliced_alignment")
    public void setNoSplicedAlignment(Long noSplicedAlignment) {
        this.noSplicedAlignment = noSplicedAlignment;
    }

    public Hisat2Params withNoSplicedAlignment(Long noSplicedAlignment) {
        this.noSplicedAlignment = noSplicedAlignment;
        return this;
    }

    @JsonProperty("transcriptome_mapping_only")
    public Long getTranscriptomeMappingOnly() {
        return transcriptomeMappingOnly;
    }

    @JsonProperty("transcriptome_mapping_only")
    public void setTranscriptomeMappingOnly(Long transcriptomeMappingOnly) {
        this.transcriptomeMappingOnly = transcriptomeMappingOnly;
    }

    public Hisat2Params withTranscriptomeMappingOnly(Long transcriptomeMappingOnly) {
        this.transcriptomeMappingOnly = transcriptomeMappingOnly;
        return this;
    }

    @JsonProperty("tailor_alignments")
    public String getTailorAlignments() {
        return tailorAlignments;
    }

    @JsonProperty("tailor_alignments")
    public void setTailorAlignments(String tailorAlignments) {
        this.tailorAlignments = tailorAlignments;
    }

    public Hisat2Params withTailorAlignments(String tailorAlignments) {
        this.tailorAlignments = tailorAlignments;
        return this;
    }

    @JsonAnyGetter
    public Map<String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public String toString() {
        return ((((((((((((((((((((((((((((((((((((("Hisat2Params"+" [wsId=")+ wsId)+", samplesetId=")+ samplesetId)+", genomeId=")+ genomeId)+", numThreads=")+ numThreads)+", qualityScore=")+ qualityScore)+", skip=")+ skip)+", trim3=")+ trim3)+", trim5=")+ trim5)+", np=")+ np)+", minins=")+ minins)+", maxins=")+ maxins)+", orientation=")+ orientation)+", minIntronLength=")+ minIntronLength)+", maxIntronLength=")+ maxIntronLength)+", noSplicedAlignment=")+ noSplicedAlignment)+", transcriptomeMappingOnly=")+ transcriptomeMappingOnly)+", tailorAlignments=")+ tailorAlignments)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
