

### Summary

Based on the code provided, this codebase appears to be a utility module for making HTTP requests and handling server-sent events (SSE) in a TypeScript environment. Here's an overall summary of the key components:

1. **Constants and Types**:
   - `ContentType`: An object containing various content type strings (e.g., `json`, `stream`, `form`, `download`, `upload`) used for setting request headers.
   - `baseOptions`: The default options object for `fetch` requests, including the mode, credentials, and headers.
   - Various type definitions for callback functions, such as `IOnData`, `IOnThought`, `IOnFile`, etc., used for handling different events in SSE responses.

2. **Utility Functions**:
   - `unicodeToChar`: A function that converts Unicode escape sequences in a string to their corresponding characters.
   - `format`: A function that formats a given text, trimming leading/trailing whitespaces and replacing newlines with `<br/>`.

3. **SSE Handling**:
   - `handleStream`: A function that processes the server-sent event stream, parsing the incoming data and invoking the appropriate callback functions (e.g., `onData`, `onThought`, `onFile`, etc.).

4. **Base Fetch Function**:
   - `baseFetch`: The main function that handles HTTP requests, taking a URL, fetch options, and additional options (e.g., `isPublicAPI`, `bodyStringify`, `needAllResponseContent`). It applies various transformations to the request and response, including handling query parameters, timeouts, and error cases.

5. **Request Methods**:
   - `request`, `get`, `post`, `put`, `del`, `patch`: Wrapper functions around `baseFetch` that provide a more convenient interface for making different types of HTTP requests (GET, POST, PUT, DELETE, PATCH) with optional public API support.

6. **Upload Function**:
   - `upload`: A function that handles file uploads, taking an options object, an optional boolean flag for public API, and optional URL and search parameters.

7. **SSE Post Function**:
   - `ssePost`: A function that initiates a server-sent event stream, taking a URL, fetch options, and various callback functions to handle the incoming data and events.

Overall, this codebase provides a consistent and abstracted interface for making HTTP requests and handling server-sent events, with support for various content types, error handling, and public API integration.

### Highlights

The key features of this code are:

1. **API Configuration**: The code imports various configuration constants, such as `API_PREFIX`, `IS_CE_EDITION`, and `PUBLIC_API_PREFIX`, which are likely used to customize the API endpoints and behavior based on the application environment.

2. **Content Types**: The code defines a `ContentType` object that specifies different content types, such as `json`, `stream`, `form`, `download`, and `upload`, which are used throughout the code.

3. **Base Fetch Options**: The code defines a `baseOptions` object that sets the default options for the fetch requests, including the HTTP method, mode, credentials, and headers.

4. **Callback Functions**: The code defines several callback functions, such as `IOnData`, `IOnThought`, `IOnFile`, `IOnMessageEnd`, `IOnMessageReplace`, `IOnAnnotationReply`, `IOnCompleted`, and `IOnError`, which are used to handle different types of responses from the API.

5. **Utility Functions**: The code includes two utility functions: `unicodeToChar` and `format`, which are used to handle string formatting and unicode character conversion.

The main purpose of this code appears to be providing a set of reusable functions for making API requests, handling different types of responses, and managing the API configuration. The code seems to be part of a larger application that utilizes these features.```python
```python
# Define constants and helper functions
CONTENT_TYPES = {
    "json": "application/json",
    "stream": "text/event-stream",
    "form": "application/x-www-form-urlencoded; charset=UTF-8",
    "download": "application/octet-stream",
    "upload": "multipart/form-data"
}

def unicode_to_char(text):
    # Convert unicode escape sequences to characters
    pass

def format_text(text):
    # Format the text (trim, replace newlines, etc.)
    pass

# Define types for callbacks
OnDataCallback = Callable[[str, bool, Dict[str, Any]], None]
OnThoughtCallback = Callable[[Dict[str, Any]], None]
OnFileCallback = Callable[[Dict[str, Any]], None]
OnMessageEndCallback = Callable[[Dict[str, Any]], None]
OnMessageReplaceCallback = Callable[[Dict[str, Any]], None]
OnAnnotationReplyCallback = Callable[[Dict[str, Any]], None]
OnCompletedCallback = Callable[[bool], None]
OnErrorCallback = Callable[[str, Optional[str]], None]

# Define base options for fetch requests
BASE_OPTIONS = {
    "method": "GET",
    "mode": "cors",
    "credentials": "include",
    "headers": {
        "Content-Type": CONTENT_TYPES["json"]
    },
    "redirect": "follow"
}

# Define the main function to handle fetch requests
def base_fetch(url, fetch_options, other_options={}):
    # Merge base options with fetch options
    options = {**BASE_OPTIONS, **fetch_options}

    # Handle authorization headers
    if other_options.get("isPublicAPI"):
        # Get shared token from URL and use it for authorization
        pass
    else:
        # Use console token for authorization
        pass

    # Handle content type
    if other_options.get("deleteContentType"):
        options["headers"].pop("Content-Type", None)
    else:
        content_type = options["headers"].get("Content-Type")
        if not content_type:
            options["headers"]["Content-Type"] = CONTENT_TYPES["json"]

    # Handle URL prefix based on public API flag
    url_prefix = other_options.get("PUBLIC_API_PREFIX") if other_options.get("isPublicAPI") else other_options.get("API_PREFIX")
    url_with_prefix = f"{url_prefix}{url if url.startswith('/') else '/' + url}"

    # Handle query parameters for GET requests
    if options["method"] == "GET" and "params" in options:
        params = options.pop("params")
        query_params = ["{}={}".format(k, urllib.parse.quote(str(v))) for k, v in params.items()]
        if "?" in url_with_prefix:
            url_with_prefix += "&" + "&".join(query_params)
        else:
            url_with_prefix += "?" + "&".join(query_params)

    # Handle request body
    if "body" in options and other_options.get("bodyStringify"):
        options["body"] = json.dumps(options["body"])

    # Handle timeout
    return Promise.race([
        # Timeout promise
        asyncio.create_task(asyncio.sleep(OTHER_OPTIONS.get("TIME_OUT", 100000))).then(
            lambda _: raise Exception("request timeout")
        ),
        # Fetch promise
        asyncio.create_task(
            fetch(url_with_prefix, options)
            .then(handle_response)
            .catch(handle_error)
        )
    ])

# Handle the response from the fetch request
def handle_response(response):
    if not response.ok:
        # Handle error responses
        return response.json().then(
            lambda data: raise ResponseError(data.get("code"), data.get("message"), response.status)
        )

    # Handle successful responses
    if response.status == 204:
        # Handle delete API responses
        return {"result": "success"}
    else:
        # Return the response data
        content_type = response.headers.get("Content-Type")
        if content_type == CONTENT_TYPES["download"]:
            return response.blob()
        else:
            return response.json()

# Handle errors from the fetch request
def handle_error(error):
    # Display error message using Toast component
    Toast.notify({"type": "error", "message": str(error)})
    raise error

# Define the main request function
def request(url, options={}, other_options={}):
    return base_fetch(url, options, other_options)

# Define the request method functions
def get(url, options={}, other_options={}):
    return request(url, {**options, "method": "GET"}, other_options)

def post(url, options={}, other_options={}):
    return request(url, {**options, "method": "POST"}, other_options)

def put(url, options={}, other_options={}):
    return request(url, {**options, "method": "PUT"}, other_options)

def delete(url, options={}, other_options={}):
    return request(url, {**options, "method": "DELETE"}, other_options)

def patch(url, options={}, other_options={}):
    return request(url, {**options, "method": "PATCH"}, other_options)

# Define the public API request functions
def get_public(url, options={}, other_options={}):
    return get(url, options, {**other_options, "isPublicAPI": True})

def post_public(url, options={}, other_options={}):
    return post(url, options, {**other_options, "isPublicAPI": True})

def put_public(url, options={}, other_options={}):
    return put(url, options, {**other_options, "isPublicAPI": True})

def delete_public(url, options={}, other_options={}):
    return delete(url, options, {**other_options, "isPublicAPI": True})

def patch_public(url, options={}, other_options={}):
    return patch(url, options, {**other_options, "isPublicAPI": True})

# Define the upload function
def upload(options, is_public_api=False, url=None, search_params=None):
    # Handle authorization for public API or console
    if is_public_api:
        # Get shared token from URL and use it for authorization
        pass
    else:
        # Use console token for authorization
        pass

    # Merge default options with the provided options
    default_options = {
        "method": "POST",
        "url": (url if url else "/files/upload") + (search_params or ""),
        "headers": {
            "Authorization": f"Bearer {token}"
        },
        "data": {}
    }
    options = {**default_options, **options}

    # Send the upload request using Promise
    return Promise(
        lambda resolve, reject: {
            # Open the XHR request
            xhr.open(options["method"], options["url"])
            # Set the request headers
            for key, value in options["headers"].items():
                xhr.setRequestHeader(key, value)
            # Set other options
            xhr.withCredentials = True
            xhr.responseType = "json"
            # Handle the response
            xhr.onreadystatechange = lambda: {
                if xhr.readyState == 4:
                    if xhr.status == 201:
                        resolve(xhr.response)
                    else:
                        reject(xhr)
            }
            # Handle progress callbacks
            xhr.upload.onprogress = options["onprogress"]
            # Send the request
            xhr.send(options["data"])
        }
    )

# Define the SSE (Server-Sent Events) POST function
def sse_post(url, fetch_options, other_options={}):
    # Create an AbortController
    abort_controller = AbortController()

    # Merge base options with fetch options
    options = {**BASE_OPTIONS, "method": "POST", "signal": abort_controller.signal, **fetch_options}

    # Handle content type
    content_type = options["headers"].get("Content-Type")
    if
```


### import Relationships

Imports found:
import { API_PREFIX, IS_CE_EDITION, PUBLIC_API_PREFIX } from '@/config'
import Toast from '@/app/components/base/toast'
import type { AnnotationReply, MessageEnd, MessageReplace, ThoughtItem } from '@/app/components/app/chat/type'
import type { VisionFile } from '@/types/app'