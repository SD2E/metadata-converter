#!/usr/bin/python
import json
import sys
import os
from jsonschema import validate
from jsonschema import ValidationError
from common import SampleConstants
import six
from jq import jq

def convert_biofab(schema_file, input_file, verbose=True, output=True):

    schema = json.load(open(schema_file))
    biofab_doc = json.load(open(input_file))

    output_doc = {}

    # TODO cannot map yet
    output_doc[SampleConstants.EXPERIMENT_ID] = biofab_doc["plan_id"]
    output_doc[SampleConstants.CHALLENGE_PROBLEM] = biofab_doc["attributes"]["challenge_problem"]
    output_doc[SampleConstants.EXPERIMENT_REFERENCE] = SampleConstants.CP_REF_UNKNOWN

    output_doc[SampleConstants.LAB] = biofab_doc["attributes"]["lab"]
    output_doc[SampleConstants.SAMPLES] = []

    for biofab_sample in biofab_doc["files"]:
        sample_doc = {}
        file_source = biofab_sample["sources"][0]
        sample_doc[SampleConstants.SAMPLE_ID] = file_source

        #print(biofab_sample)
        #print(file_source) 
        item = jq(".items[] | select(.item_id==\"" + file_source + "\")").transform(biofab_doc)
        
        # plate this source is a part of?
        #print(item) 
        part_of_attr = "part_of"
        if part_of_attr not in item:
            print("TODO, parse: {}".format(file_source))
            continue

        part_of = item[part_of_attr]
        plate = jq(".items[] | select(.item_id==\"" + part_of + "\")").transform(biofab_doc)

        #print(plate)
        reagents = []

        media_attr = "type_of_media"
        if media_attr not in plate:
            # try one more lookup
            plate_source = plate["sources"][0]
            plate_source_lookup = jq(".items[] | select(.item_id==\"" + plate_source + "\")").transform(biofab_doc)
            # TODO librarian mapping
            #print(plate_source_lookup)
            reagents.append(plate_source_lookup["attributes"][media_attr])
            temperature = plate_source_lookup["attributes"]["growth_temperature"]
            sample_doc[SampleConstants.TEMPERATURE] = str(temperature) + ":celsius"
        else:
            # TODO librarian mapping
            reagents.append(plate[media_attr])
            temperature = plate["attributes"]["growth_temperature"]
            sample_doc[SampleConstants.TEMPERATURE] = temperature + ":celsius"
            raise Exception("foo")
        sample_doc[SampleConstants.CONTENTS] = reagents

        
        # TODO librarian mapping
        # could use ID
        #print(item)
        strain = item["sample"]["sample_name"]
        sample_doc[SampleConstants.STRAIN] = strain

        # TODO replicate
        # Compute this? Biofab knows the number of replicates, but does not individually tag...
        # "name": "Biological Replicates",
        #  "field_value_id": "451711",
        #  "value": "6"

        # skip controls for now
        """    
        control_for_prop = "control_for_samples"
        sbh_uri_prop = "SD2_SBH_URI"
        if control_for_prop in biofab_sample:
            control_for_val = biofab_sample[control_for_prop]

            #int -> str conversion
            if isinstance(control_for_val, list):
                if type(control_for_val[0]) == int:
                    control_for_val = [str(n) for n in control_for_val]

            if sbh_uri_prop in props:
                sbh_uri_val = props[sbh_uri_prop]
                if "fluorescein_control" in sbh_uri_val:
                    sample_doc[SampleConstants.STANDARD_TYPE] = SampleConstants.STANDARD_FLUORESCEIN
                    sample_doc[SampleConstants.STANDARD_FOR] = control_for_val
                else:
                    print("Unknown control for sample: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
            else:
                print("Unknown control for sample: {}".format(sample_doc[SampleConstants.SAMPLE_ID]))
        """
        measurement_doc = {}
        #print(part_of)
        try:
            time_val = jq(".operations[] | select(.inputs[].item_id ==\"" + part_of + "\").inputs[] | select (.name == \"Timepoint (hr)\").value").transform(biofab_doc)
            measurement_doc[SampleConstants.TIMEPOINT] = time_val + ":hour"
        except StopIteration:
            print("Warning: Could not find matching time value for {}".format(part_of))

        measurement_doc[SampleConstants.FILES] = []

        assay_type = biofab_sample["type"]
        if assay_type == "FCS": 
            measurement_type = SampleConstants.MT_FLOW
        else:
            raise ValueError("Could not parse MT: {}".format(assay_type))

        measurement_doc[SampleConstants.MEASUREMENT_TYPE] = measurement_type
        
        # TODO
        #measurement_doc[SampleConstants.MEASUREMENT_NAME] = measurement_props["measurement_name"]
        file_name = biofab_sample["filename"]
        file_type = SampleConstants.infer_file_type(file_name)
        measurement_doc[SampleConstants.FILES].append(
                            { SampleConstants.M_NAME : file_name, \
                            SampleConstants.M_TYPE : file_type, \
                            SampleConstants.M_STATE : SampleConstants.M_STATE_RAW})

        if len(measurement_doc[SampleConstants.FILES]) == 0:
            print("Warning, measurement contains no files, skipping {}".format(measurement_key))
        else:
            if SampleConstants.MEASUREMENTS not in sample_doc:
                sample_doc[SampleConstants.MEASUREMENTS] = []
            sample_doc[SampleConstants.MEASUREMENTS].append(measurement_doc)

        output_doc[SampleConstants.SAMPLES].append(sample_doc)

    try:
        validate(output_doc, schema)
        #if verbose:
            #print(json.dumps(output_doc, indent=4))
        if output:
            path = os.path.join("output/biofab", os.path.basename(input_file))
            with open(path, 'w') as outfile:
                json.dump(output_doc, outfile, indent=4)
        return True
    except ValidationError as err:
        if verbose:
            print("Schema Validation Error: {0}\n".format(err))
        return False

if __name__ == "__main__":
    path = sys.argv[2]
    if os.path.isdir(path):
        for f in os.listdir(path):
            file_path = os.path.join(path, f)
            print(file_path)
            if file_path.endswith(".js") or file_path.endswith(".json"):
                convert_biofab(sys.argv[1], file_path)
            else:
                print("Skipping {}".format(file_path))
    else:
        convert_biofab(sys.argv[1], sys.argv[2])
