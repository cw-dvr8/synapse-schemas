#!/usr/bin/env python3

"""
Program: PEC_high_value_keys.py

Purpose: Validate a PEC fileview to make sure that high value keys contain
         data.

Input parameters: SynID for the fileview
                  Name (including organization) of the validation schema
                  Output filename

Outputs: Output file

Execution: PEC_high_value_keys.py <fileview SynID> <validation schema>
               <output file>

"""

import argparse
import jsonschema
import pandas as pd
import synapseclient
import schema_tools

def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("fileview_synid", type=str,
                        help="Synapse ID of the fileview")
    parser.add_argument("val_schema", type=str,
                        help="Name (including organization) of the validation schema")
    parser.add_argument("output_file", type=str,
                        help="Output file base name")

    args = parser.parse_args()

    syn = synapseclient.Synapse()
    syn.login(silent=True)

    row_error = ""
    error_dict = {}
    val_error_df = pd.DataFrame()

    # Get the JSON validation schema, dereference it, and create a validator.
    syn_schema = syn.restGET(f"/schema/type/registered/{args.val_schema}")
    deref_schema = schema_tools.syn_deref(syn_schema)

    # Synapse does not support the required keyword yet.
    deref_schema["required"] = ["assay", "cellType", "dataType", "fileFormat", "nucleicAcidSource", "referenceSet", "species", "study", "tissue"]
    schema_validator = jsonschema.Draft7Validator(deref_schema)

    # Query the fileview for the high value keys.
    query_stmt = f'SELECT assay, cellType, dataSubtype, dataType, fileFormat, id, nucleicAcidSource, parentId, referenceSet, species, study, tissue FROM {args.fileview_synid}'
    query_nan_df = syn.tableQuery(query_stmt).asDataFrame()

    # Pandas reads in empty fields as nan. Replace nan with None.
    query_df = query_nan_df.where(query_nan_df.notnull(), None).copy()

    # The Synapse query is returning the study as a character string that 
    # looks like '["iPSC"]'.  Strip out the brackets and the double quotes.
    query_df["study"] = query_df["study"].str.strip('["]')

    data_dict_list = query_df.to_dict(orient="records")

    for data_record in data_dict_list:

        # Remove any None values from the dictionary - it simplifies the
        # coding of the JSON validation schema.
        clean_record = {k: data_record[k] for k in data_record if data_record[k] is not None}

        schema_errors = schema_validator.iter_errors(clean_record)

        row_error = schema_tools.validation_errors(schema_errors)

        if row_error:
            error_dict["SynID"] = clean_record["id"]
            error_dict["parentId"] = clean_record["parentId"]
            error_dict["returned_error"] = row_error
            val_error_df = val_error_df.append(error_dict, ignore_index=True)

    # The validator returns a single string for all of the errors found for
    # each record, so turn the string into a list and then explode it.
    val_error_df["errormsg"] = val_error_df["returned_error"].str.split("\n")
    val_error_df = val_error_df.explode("errormsg")

    # Write out the list of unique errors.
    output_file_name = f"{args.output_file}_unique_errors.csv"
    error_file = open(output_file_name)
    unique_errors = val_error_df.groupby("errormsg")["errormsg"].count()
    unique_errors.to_csv(error_file)
    error_file.close()

    # Write out the list of unique errors by Synapse parent ID.
    output_file_name = f"{args.output_file}_SynParent_errors.csv"
    error_file = open(output_file_name)
    syn_parent_errors = val_error_df.groupby(["parentId", "errormsg"])["errormsg"].count()
    syn_parent_errors.to_csv(error_file)
    error_file.close()


if __name__ == "__main__":
    main()
