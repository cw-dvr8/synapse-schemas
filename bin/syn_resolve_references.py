def syn_resolve_references(json_schema):

    """
    Function: syn_resolve_references

    Purpose: Resolves $ref statements referring to schemas registered in
             Synapse.

    Arguments: JSON schema to be de-referenced

    Returns: A de-referenced JSON schema in dictionary form

    """

    import jsonschema

    # The full URL is defined in the Synapse docs.
    syn_url = "https://repo-prod.prod.sagebase.org/repo/v1/schema/type/registered"

    ref_resolver = jsonschema.RefResolver.from_schema(json_schema)

    for schema_key in json_schema["properties"]:
        if "$ref" in json_schema["properties"][schema_key]:
            ref_url = f"{syn_url}/{json_schema['properties'][schema_key]['$ref']}"
            deref_object = ref_resolver.resolve(ref_url)
            json_schema["properties"][schema_key] = deref_object[1]

    return(json_schema)
