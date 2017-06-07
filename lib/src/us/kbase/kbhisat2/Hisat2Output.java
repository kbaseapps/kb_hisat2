
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
 * <p>Original spec-file type: Hisat2Output</p>
 * <pre>
 * Output for hisat2.
 * alignment_ref: can be either an Alignment or AlignmentSet, depending on inputs.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report_name",
    "report_ref",
    "alignment_ref"
})
public class Hisat2Output {

    @JsonProperty("report_name")
    private String reportName;
    @JsonProperty("report_ref")
    private String reportRef;
    @JsonProperty("alignment_ref")
    private String alignmentRef;
    private Map<String, Object> additionalProperties = new HashMap<String, Object>();

    @JsonProperty("report_name")
    public String getReportName() {
        return reportName;
    }

    @JsonProperty("report_name")
    public void setReportName(String reportName) {
        this.reportName = reportName;
    }

    public Hisat2Output withReportName(String reportName) {
        this.reportName = reportName;
        return this;
    }

    @JsonProperty("report_ref")
    public String getReportRef() {
        return reportRef;
    }

    @JsonProperty("report_ref")
    public void setReportRef(String reportRef) {
        this.reportRef = reportRef;
    }

    public Hisat2Output withReportRef(String reportRef) {
        this.reportRef = reportRef;
        return this;
    }

    @JsonProperty("alignment_ref")
    public String getAlignmentRef() {
        return alignmentRef;
    }

    @JsonProperty("alignment_ref")
    public void setAlignmentRef(String alignmentRef) {
        this.alignmentRef = alignmentRef;
    }

    public Hisat2Output withAlignmentRef(String alignmentRef) {
        this.alignmentRef = alignmentRef;
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
        return ((((((((("Hisat2Output"+" [reportName=")+ reportName)+", reportRef=")+ reportRef)+", alignmentRef=")+ alignmentRef)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
