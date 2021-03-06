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

# Get a list of organizations
organization_list = syn.restPOST("/schema/organization/list", json.dumps({"body": ""}))

# Register an organization in Synapse
organization = syn.restPOST('/schema/organization', json.dumps({'organizationName': 'sage.annotations'}))

# Get a list of schemas for the organization cmolitor.test.
schema_list = syn.restPOST("/schema/list", json.dumps({"organizationName": "cmolitor.test"}))
# If there is more than one page in the list, get the next page.
schema_list2 = syn.restPOST("/schema/list", json.dumps({"organizationName": "cmolitor.test", "nextPageToken": schema_list['nextPageToken']}))

# Deleting a schema.
schema_delete = syn.restDELETE("/schema/type/registered/cmolitor.test-assayValidation.baseAssayNoInt")

# Registering a schema in Synapse.
ref_schema = json.load(open("assayrnaSeqNoInt.json", "r"))
create_schema_result = syn._waitForAsync("/schema/type/create/async", {"schema": ref_schema})

# Get a schema that has been registered in Synapse.
val_schema = syn.restGET("/schema/type/registered/cmolitor.test-assayValidation.assayrnaSeqNoInt")

# Get a dereferenced schema that has been registered in Synapse.
val_schema = syn._waitForAsync("/schema/type/validation/async", {"$id": "cmolitor.test-assayValidation.assayrnaSeqNoInt"})

# Get the ACL for an organization - need to get a list of organizations first in
# order to get the organization ID (47, in this case)
schema_acl = syn.restGet("/schema/organization/47/acl")

# Modify the ACL for an organization - need to get a list of organizations first
# in order to get the organization ID (47, in this case). Get the current ACL
# as referenced above. Also have to get the Synapse ID of the person getting
# added.
new_access = {}
new_access["principalId"] = 3368956
new_access["accessType"] = ["DELETE","UPDATE","CHANGE_PERMISSIONS","CREATE","READ"]
schema_acl["resourceAccess"].append(new_access)
new_schema_acl = syn.restPUT("/schema/organization/47/acl", json.dumps(schema_acl))
