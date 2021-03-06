
"""Some constants to populate samples-schema.json
   compliant outputs
"""
class SampleConstants():

    """Obvious issues with this, welcome something more robust.
    """
    def infer_file_type(file_name):

        if file_name.endswith("fastq.gz"):
            return SampleConstants.F_TYPE_FASTQ
        elif file_name.endswith("zip"):
            return SampleConstants.F_TYPE_ZIP
        elif file_name.endswith("fcs"):
            return SampleConstants.F_TYPE_FCS
        elif file_name.endswith("sraw"):
            return SampleConstants.F_TYPE_SRAW
        elif file_name.endswith("txt"):
            return SampleConstants.F_TYPE_TXT
        elif file_name.endswith("csv"):
            return SampleConstants.F_TYPE_CSV
        elif file_name.endswith("mzML"):
            return SampleConstants.F_TYPE_MZML
        elif file_name.endswith("msf"):
            return SampleConstants.F_TYPE_MSF
        else:
            raise ValueError("Could not parse FT: {}".format(file_name))

    #experiment
    EXPERIMENT_ID = "experiment_id"
    CHALLENGE_PROBLEM = "challenge_problem"

    CP_REF_UNKNOWN = "Unknown"

    EXPERIMENT_REFERENCE = "experiment_reference"
    LAB = "lab"
    LAB_GINKGO = "Ginkgo"
    LAB_TX = "Transcriptic"
    LAB_UWBF = "UWBF"

    #samples
    SAMPLES = "samples"
    SAMPLE_ID = "sample_id"
    STRAIN = "strain"
    CONTENTS = "contents"
    REPLICATE = "replicate"
    INOCULATION_DENSITY = "inoculation_density"
    TEMPERATURE = "temperature"
    TIMEPOINT = "timepoint"

    STANDARD_TYPE = "standard_type"
    STANDARD_FOR = "standard_for"
    STANDARD_FLUORESCEIN = "FLUORESCEIN"

    #measurements
    MEASUREMENTS = "measurements"
    FILES = "files"
    MEASUREMENT_TYPE = "measurement_type"
    MEASUREMENT_NAME = "measurement_name"
    MEASUREMENT_TMT_CHANNEL = "TMT_channel"
    MT_RNA_SEQ = "RNA_SEQ"
    MT_FLOW = "FLOW"
    MT_PLATE_READER = "PLATE_READER"
    MT_PROTEOMICS = "PROTEOMICS"
    M_NAME = "name"
    M_TYPE = "type"
    M_STATE = "state"
    M_STATE_RAW = "RAW"
    M_STATE_PROCESSED = "PROCESSED"

    F_TYPE_SRAW = "SRAW"
    F_TYPE_FASTQ = "FASTQ"
    F_TYPE_CSV = "CSV"
    F_TYPE_FCS = "FCS"
    F_TYPE_ZIP = "ZIP"
    F_TYPE_TXT = "TXT"
    F_TYPE_MZML = "MZML"
    F_TYPE_MSF = "MSF"




