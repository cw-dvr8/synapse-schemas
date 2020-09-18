"""
This is not an actual program per se, it is just a place for me to write down
various API calls that I make so that I remember how to do it, seeing as how
I don't have a lot of experience with APIs.
"""

import json
import jsonschema
import synapseclient

syn = synapseclient.Synapse()
syn.login(silent=True)

# Get a list of schemas for the organization cmolitor.test.
schema_list = syn.restPOST("/schema/list", json.dumps({"organizationName": "cmolitor.test"}))

# Registering a schema in Synapse.
ref_schema = json.load(open("assayrnaSeqNoInt.json", "r"))
create_schema_result = syn._waitForAsync("/schema/type/create/async", {"schema": ref_schema})

# Get a schema that has been registered in Synapse.
val_schema = syn.restGET("/schema/type/registered/cmolitor.test-assayValidation.assayrnaSeqNoInt")

# Get a dereferenced schema that has been registered in Synapse.
val_schema = syn._waitForAsync("/schema/type/validation/async", {"$id": "cmolitor.test-assayValidation.assayrnaSeqNoInt"})