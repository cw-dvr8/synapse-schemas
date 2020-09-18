def syn_deref(json_schema, first_call=True):

    """
    Function: syn_deref

    Purpose: Walks through allOf and properties statements in the input
             schema to resolve references.

    Arguments: JSON schema to be de-referenced

    Returns: A completely de-referenced JSON schema in dictionary form

    """

    import jsonschema

    ref_resolver = jsonschema.RefResolver.from_schema(json_schema)

    # The full URL is defined in the Synapse docs.
    syn_url = "https://repo-prod.prod.sagebase.org/repo/v1/schema/type/registered"

    # Resolve references in the schema properties.
    if "properties" in json_schema:
        for schema_key in json_schema["properties"]:
            if "$ref" in json_schema["properties"][schema_key]:
                property_ref_url = f"{syn_url}/{json_schema['properties'][schema_key]['$ref']}"
                deref_object = ref_resolver.resolve(property_ref_url)
                json_schema["properties"][schema_key] = deref_object[1]

    # If there is an allOf section in the schema, resolve it all of the way
    # down and then add all keys to the schema properties section.
    if "allOf" in json_schema:
        for allOf_entry in json_schema["allOf"]:
            if "$ref" in allOf_entry:
                allOf_ref_url = f"{syn_url}/{allOf_entry['$ref']}"
                allOf_schema = ref_resolver.resolve(allOf_ref_url)[1]
                allOf_entry = syn_deref(allOf_schema, False)
        if "properties" in json_schema:
            json_schema["properties"].update(allOf_entry["properties"])
        else:
            json_schema["properties"] = allOf_entry["properties"]

    # If it is the first call to the function, return the whole schema.
    # section.
    if first_call:
        return_schema = json_schema

        # Any allOf section will have been resolved so we do not need it in
        # the validation schema.
        return_schema.pop("allOf", None)

    # If it is one of the recursive calls, we are only interested in the
    # properties section.
    else:
        return_schema = {}
        return_schema["properties"] = json_schema["properties"]

    return(return_schema)
