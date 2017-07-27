
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
 * alignmentset_ref if an alignment set is created
 * alignment_objs for each individual alignment created. The keys are the references to the reads
 *     object being aligned.
 * </pre>
 * 
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
@Generated("com.googlecode.jsonschema2pojo")
@JsonPropertyOrder({
    "report_name",
    "report_ref",
    "alignmentset_ref",
    "alignment_objs"
})
public class Hisat2Output {

    @JsonProperty("report_name")
    private java.lang.String reportName;
    @JsonProperty("report_ref")
    private java.lang.String reportRef;
    @JsonProperty("alignmentset_ref")
    private java.lang.String alignmentsetRef;
    @JsonProperty("alignment_objs")
    private Map<String, AlignmentObj> alignmentObjs;
    private Map<java.lang.String, Object> additionalProperties = new HashMap<java.lang.String, Object>();

    @JsonProperty("report_name")
    public java.lang.String getReportName() {
        return reportName;
    }

    @JsonProperty("report_name")
    public void setReportName(java.lang.String reportName) {
        this.reportName = reportName;
    }

    public Hisat2Output withReportName(java.lang.String reportName) {
        this.reportName = reportName;
        return this;
    }

    @JsonProperty("report_ref")
    public java.lang.String getReportRef() {
        return reportRef;
    }

    @JsonProperty("report_ref")
    public void setReportRef(java.lang.String reportRef) {
        this.reportRef = reportRef;
    }

    public Hisat2Output withReportRef(java.lang.String reportRef) {
        this.reportRef = reportRef;
        return this;
    }

    @JsonProperty("alignmentset_ref")
    public java.lang.String getAlignmentsetRef() {
        return alignmentsetRef;
    }

    @JsonProperty("alignmentset_ref")
    public void setAlignmentsetRef(java.lang.String alignmentsetRef) {
        this.alignmentsetRef = alignmentsetRef;
    }

    public Hisat2Output withAlignmentsetRef(java.lang.String alignmentsetRef) {
        this.alignmentsetRef = alignmentsetRef;
        return this;
    }

    @JsonProperty("alignment_objs")
    public Map<String, AlignmentObj> getAlignmentObjs() {
        return alignmentObjs;
    }

    @JsonProperty("alignment_objs")
    public void setAlignmentObjs(Map<String, AlignmentObj> alignmentObjs) {
        this.alignmentObjs = alignmentObjs;
    }

    public Hisat2Output withAlignmentObjs(Map<String, AlignmentObj> alignmentObjs) {
        this.alignmentObjs = alignmentObjs;
        return this;
    }

    @JsonAnyGetter
    public Map<java.lang.String, Object> getAdditionalProperties() {
        return this.additionalProperties;
    }

    @JsonAnySetter
    public void setAdditionalProperties(java.lang.String name, Object value) {
        this.additionalProperties.put(name, value);
    }

    @Override
    public java.lang.String toString() {
        return ((((((((((("Hisat2Output"+" [reportName=")+ reportName)+", reportRef=")+ reportRef)+", alignmentsetRef=")+ alignmentsetRef)+", alignmentObjs=")+ alignmentObjs)+", additionalProperties=")+ additionalProperties)+"]");
    }

}
