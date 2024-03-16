

### Summary

This codebase appears to be a set of utility functions and API calls related to managing tools and collections in a workspace. Here's an overall summary:

1. **Fetching Data**:
   - `fetchCollectionList()`: Fetches the list of tool provider collections.
   - `fetchBuiltInToolList(collectionName)`: Fetches the list of built-in tools for a specific collection.
   - `fetchCustomToolList(collectionName)`: Fetches the list of custom tools for a specific collection.
   - `fetchModelToolList(collectionName)`: Fetches the list of model tools for a specific collection.
   - `fetchBuiltInToolCredentialSchema(collectionName)`: Fetches the credential schema for built-in tools in a specific collection.
   - `fetchCustomCollection(collectionName)`: Fetches the details of a custom collection.

2. **Updating Data**:
   - `updateBuiltInToolCredential(collectionName, credential)`: Updates the credential for a built-in tool in a specific collection.
   - `removeBuiltInToolCredential(collectionName)`: Removes the credential for a built-in tool in a specific collection.
   - `createCustomCollection(collection)`: Creates a new custom collection.
   - `updateCustomCollection(collection)`: Updates an existing custom collection.
   - `removeCustomCollection(collectionName)`: Deletes a custom collection.

3. **Parsing and Testing**:
   - `parseParamsSchema(schema)`: Parses a parameter schema and returns the parameter schema and schema type.
   - `importSchemaFromURL(url)`: Imports a schema from a remote URL.
   - `testAPIAvailable(payload)`: Tests the availability of an API with the provided payload.

Overall, this codebase seems to be managing the lifecycle of tools and collections, including fetching data, updating credentials, and performing various CRUD operations on custom collections.

### Highlights

The key features of this code are:

1. **API Interaction**: The code exports several functions that interact with an API to fetch and manipulate data related to tool collections, built-in tools, custom tools, and tool credentials.

2. **Fetching Data**: The code exports functions like `fetchCollectionList`, `fetchBuiltInToolList`, `fetchCustomToolList`, `fetchModelToolList`, and `fetchCustomCollection` that fetch data from the API.

3. **Updating Data**: The code exports functions like `updateBuiltInToolCredential`, `createCustomCollection`, `updateCustomCollection`, and `removeCustomCollection` that update data on the API.

4. **Parsing Schemas**: The `parseParamsSchema` function is used to parse a custom parameter schema from the API.

5. **API Testing**: The `testAPIAvailable` function is used to test the availability of the API.

The key thing to look for in this code is the interaction with the API to manage tool-related data, including fetching, updating, and parsing data from the API. The code provides a set of utility functions that abstract away the API calls, making it easier to work with the tool-related data in the application.```python
```python
# Define functions for fetching data from the API

def fetch_collection_list():
    """
    Fetches the list of collections from the API.
    Returns:
        A list of collections.
    """
    return get('/workspaces/current/tool-providers')

def fetch_builtin_tool_list(collection_name):
    """
    Fetches the list of built-in tools for a given collection.
    Args:
        collection_name (str): The name of the collection.
    Returns:
        A list of tools.
    """
    return get(f'/workspaces/current/tool-provider/builtin/{collection_name}/tools')

def fetch_custom_tool_list(collection_name):
    """
    Fetches the list of custom tools for a given collection.
    Args:
        collection_name (str): The name of the collection.
    Returns:
        A list of tools.
    """
    return get(f'/workspaces/current/tool-provider/api/tools?provider={collection_name}')

def fetch_model_tool_list(collection_name):
    """
    Fetches the list of model tools for a given collection.
    Args:
        collection_name (str): The name of the collection.
    Returns:
        A list of tools.
    """
    return get(f'/workspaces/current/tool-provider/model/tools?provider={collection_name}')

def fetch_builtin_tool_credential_schema(collection_name):
    """
    Fetches the credential schema for built-in tools in a given collection.
    Args:
        collection_name (str): The name of the collection.
    Returns:
        A list of tool credential schemas.
    """
    return get(f'/workspaces/current/tool-provider/builtin/{collection_name}/credentials_schema')

def update_builtin_tool_credential(collection_name, credential):
    """
    Updates the credentials for a built-in tool in a given collection.
    Args:
        collection_name (str): The name of the collection.
        credential (dict): The new credential data.
    """
    return post(f'/workspaces/current/tool-provider/builtin/{collection_name}/update', body={'credentials': credential})

def remove_builtin_tool_credential(collection_name):
    """
    Removes the credentials for a built-in tool in a given collection.
    Args:
        collection_name (str): The name of the collection.
    """
    return post(f'/workspaces/current/tool-provider/builtin/{collection_name}/delete', body={})

def parse_params_schema(schema):
    """
    Parses a parameter schema and returns the schema details.
    Args:
        schema (str): The schema to be parsed.
    Returns:
        A dictionary containing the parameter schema and the schema type.
    """
    return post('/workspaces/current/tool-provider/api/schema', body={'schema': schema})

def fetch_custom_collection(collection_name):
    """
    Fetches the details of a custom collection.
    Args:
        collection_name (str): The name of the custom collection.
    Returns:
        The details of the custom collection.
    """
    return get(f'/workspaces/current/tool-provider/api/get?provider={collection_name}')

def create_custom_collection(collection):
    """
    Creates a new custom collection.
    Args:
        collection (dict): The details of the new custom collection.
    """
    return post('/workspaces/current/tool-provider/api/add', body=collection)

def update_custom_collection(collection):
    """
    Updates an existing custom collection.
    Args:
        collection (dict): The updated details of the custom collection.
    """
    return post('/workspaces/current/tool-provider/api/update', body=collection)

def remove_custom_collection(collection_name):
    """
    Removes a custom collection.
    Args:
        collection_name (str): The name of the custom collection to be removed.
    """
    return post('/workspaces/current/tool-provider/api/delete', body={'provider': collection_name})

def import_schema_from_url(url):
    """
    Imports a schema from a given URL.
    Args:
        url (str): The URL of the schema to be imported.
    Returns:
        The imported schema.
    """
    return get('/workspaces/current/tool-provider/api/remote', params={'url': url})

def test_api_available(payload):
    """
    Tests the availability of the API with the given payload.
    Args:
        payload (dict): The payload to be used for the API test.
    """
    return post('/workspaces/current/tool-provider/api/test/pre', body=payload)
```

This pseudocode provides a high-level overview of the functionality of the `tools.ts` file. It defines a set of functions that interact with the API to perform various tasks, such as fetching collections, tools, and credentials, as well as managing custom collections and testing API availability. Each function is accompanied by a concise description of its purpose and the input and output parameters. The code is written in a Pythonic style, using clear and descriptive function names, docstrings, and type annotations.
```


### import Relationships

Imports found:
import { get, post } from './base'
import type { Collection, CustomCollectionBackend, CustomParamSchema, Tool, ToolCredential } from '@/app/components/tools/types'