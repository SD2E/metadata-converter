#!/usr/bin/python
import json
import sys
import os
from jsonschema import validate
from jsonschema import ValidationError
from common import SampleConstants

def convert_ginkgo(schema_file, input_file, verbose=True, output=True):

    schema = json.load(open(schema_file))
    ginkgo_doc = json.load(open(input_file))

    output_doc = {}

    # TODO cannot map yet
    output_doc[SampleConstants.EXPERIMENT_ID] = "UNKNOWN"
    output_doc[SampleConstants.CHALLENGE_PROBLEM] = "UNKNOWN"
    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = "UNKNOWN"

    output_doc[SampleConstants.LAB] = SampleConstants.LAB_GINKGO
    output_doc[SampleConstants.SAMPLES] = []

    for gingko_sample in ginkgo_doc:
        sample_doc = {}
        sample_doc[SampleConstants.SAMPLE_ID] = str(gingko_sample["sample_id"])

        reagents = []
        for reagent in gingko_sample["content"]["reagent"]:
            # TODO librarian mapping
            reagents.append(reagent["name"])
        sample_doc[SampleConstants.MEDIA] = reagents

        for strain in gingko_sample["content"]["strain"]:
            # TODO librarian mapping
            sample_doc[SampleConstants.STRAIN] = strain["name"]
            # TODO multiple strains?
            continue

        # do some cleaning
        temperature = gingko_sample["properties"]["SD2_incubation_temperature"]
        if "centigrade" in temperature:
            temperature = temperature.replace("centigrade", "celsius")

        sample_doc[SampleConstants.TEMPERATURE] = temperature
        sample_doc[SampleConstants.REPLICATE] = gingko_sample["properties"]["SD2_replicate"]

        sample_doc[SampleConstants.MEASUREMENTS] = []

        for measurement_key in gingko_sample["measurements"].keys():
            measurement_doc = {}
            measurement_doc[SampleConstants.TIMEPOINT] = gingko_sample["properties"]["SD2_timepoint"]
            measurement_doc[SampleConstants.FILES] = []

            assay_type = gingko_sample["measurements"][measurement_key]["assay_type"]
            if assay_type == "NGS (RNA)":
                measurement_type = SampleConstants.MT_RNA_SEQ
            elif assay_type == "FACS":
                measurement_type = SampleConstants.MT_FLOW
            elif assay_type == "Plate Reader Assay":
                measurement_type = SampleConstants.MT_PLATE_READER
            elif assay_type == "Global Proteomics":
                measurement_type = SampleConstants.MT_PROTEOMICS
            else:
                raise ValueError("Could not parse MT: {}".format(assay_type))

            measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type
            measurement_doc[SampleConstants.MEASUREMENT_NAME] = gingko_sample["measurements"][measurement_key]["measurement_name"]

            for key in gingko_sample["measurements"][measurement_key]["dataset_files"].keys():
                if key == "processed":
                    for processed in gingko_sample["measurements"][measurement_key]["dataset_files"]["processed"]:
                        for sub_processed in processed:
                            file_type = infer_file_type(sub_processed)
                            measurement_doc[SampleConstants.FILES].append(
                                { SampleConstants.M_NAME : sub_processed, \
                                SampleConstants.M_TYPE : file_type, \
                                SampleConstants.M_STATE : SampleConstants.M_STATE_PROCESSED})
                elif key == "raw":
                    for raw in gingko_sample["measurements"][measurement_key]["dataset_files"]["raw"]:
                        for sub_raw in raw:
                            file_type = infer_file_type(sub_raw)
                            measurement_doc[SampleConstants.FILES].append(
                                { SampleConstants.M_NAME : sub_raw, \
                                SampleConstants.M_TYPE : file_type,
                                SampleConstants.M_STATE : SampleConstants.M_STATE_RAW})
                else:
                    raise ValueError("Unknown measurement type: {}".format(key))

            if len(measurement_doc[SampleConstants.FILES]) == 0:
                print("Warning, measurement contains no files, skipping {}".format(measurement_key))
            else:
                sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)

        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    try:
        validate(output_doc, schema)
        if verbose:
            print(json.dumps(output_doc, indent=4))
        if output:
            path = os.path.join("output", os.path.basename(input_file))
            with open(path, 'w') as outfile:
                json.dump(output_doc, outfile, indent=4)
        return True
    except ValidationError as err:
        if verbose:
            print("Schema Validation Error: {0}\n".format(err))
        return False

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


if __name__ == "__main__":
    path = sys.argv[2]
    if os.path.isdir(path):
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            print(file_path)
            convert_ginkgo(sys.argv[1], file_path)
    else:
        convert_ginkgo(sys.argv[1], sys.argv[2])
