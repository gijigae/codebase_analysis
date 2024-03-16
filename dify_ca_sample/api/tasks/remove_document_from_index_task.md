

### Summary

This codebase seems to be a Celery task that removes a document from an index. Here's a summary of the code:

1. **remove_document_from_index_task**: This is a Celery shared task that is responsible for removing a document from the index. It takes a `document_id` as an argument.

2. The task first retrieves the document from the database using the `Document` model. If the document is not found, it raises a `NotFound` exception.

3. If the `indexing_status` of the document is not "completed", the task simply returns without doing anything.

4. It then retrieves the dataset associated with the document. If the document has no dataset, it raises an exception.

5. The task then initializes an `IndexProcessor` using the `IndexProcessorFactory` and the document's `doc_form` attribute.

6. It retrieves all the `DocumentSegment` objects associated with the document and gets the `index_node_id` values for each segment.

7. If there are any `index_node_id` values, the task calls the `clean` method of the `IndexProcessor` with the dataset and the `index_node_id` values as arguments. This is likely where the actual removal of the document from the index happens.

8. If any exceptions occur during the process, the task logs the error and sets the `enabled` flag of the document to `True` (in case it was disabled due to the error).

9. Finally, the task deletes the `indexing_cache_key` from the Redis client.

Overall, this codebase provides a way to asynchronously remove a document from an index, handling errors and updating the document's status accordingly.

### Highlights

Here are the key features of the provided code:

1. **Asynchronous Task**: The code defines a Celery shared task named `remove_document_from_index_task`, which runs asynchronously in the background to remove a document from the index.

2. **Database and Cache Interaction**: The code interacts with the database (using `db.session`) to fetch the document and its segments. It also interacts with Redis (using `redis_client`) to manage an indexing cache key.

3. **Index Processor**: The code uses the `IndexProcessorFactory` to initialize an index processor specific to the document's form. This processor is then used to clean the index for the document's segments.

4. **Error Handling**: The code includes robust error handling, catching and logging any exceptions that may occur during the task execution. If the document is not archived, it is re-enabled in the database.

5. **Logging and Timing**: The code uses logging extensively to provide detailed information about the task execution, including the start and end times, and the document ID being processed.

The key thing to look for in this code is the overall structure and flow of the asynchronous task, which includes fetching the document from the database, interacting with the index processor, and managing the indexing cache. The error handling and logging mechanisms are also important to ensure the task can be monitored and debugged effectively.```python
```python
# Define a function to remove a document from the index
def remove_document_from_index(document_id):
    # Log the start of the process
    log_info(f"Start removing document segments from index: {document_id}")
    start_time = get_current_time()

    # Fetch the document from the database
    document = get_document_by_id(document_id)
    if not document:
        # Raise an exception if the document is not found
        raise NotFound("Document not found")

    # Check if the document has been indexed
    if document.indexing_status != "completed":
        # If not, return without doing anything
        return

    # Get the cache key for the document's indexing status
    indexing_cache_key = f"document_{document.id}_indexing"

    try:
        # Get the dataset associated with the document
        dataset = document.dataset
        if not dataset:
            # Raise an exception if the document has no dataset
            raise Exception("Document has no dataset")

        # Get the appropriate index processor for the document's format
        index_processor = get_index_processor_for_document_format(document.doc_form)

        # Fetch all the segments associated with the document
        segments = get_document_segments_by_document_id(document.id)
        index_node_ids = [segment.index_node_id for segment in segments]

        # If there are any index node IDs, clean them from the index
        if index_node_ids:
            try:
                index_processor.clean(dataset, index_node_ids)
            except Exception:
                # Log an exception if cleaning the index fails
                log_exception(f"Clean dataset {dataset.id} from index failed")

        # Log the completion of the process
        end_time = get_current_time()
        log_info(f"Document removed from index: {document.id} | Latency: {end_time - start_time}")
    except Exception:
        # Log an exception if removing the document from the index fails
        log_exception("Remove document from index failed")
        if not document.archived:
            # If the document is not archived, re-enable it
            document.enabled = True
            save_document(document)
    finally:
        # Delete the indexing cache key
        delete_redis_key(indexing_cache_key)

# Define a Celery task to remove a document from the index asynchronously
@shared_task(queue='dataset')
def remove_document_from_index_task(document_id):
    """
    Async Remove document from index
    :param document_id: document id

    Usage: remove_document_from_index.delay(document_id)
    """
    remove_document_from_index(document_id)
```

Explanation:
1. The `remove_document_from_index` function is the main logic for removing a document from the index.
2. It first logs the start of the process and gets the current time.
3. It then fetches the document from the database, and if the document is not found, it raises a `NotFound` exception.
4. If the document has not been indexed, it returns without doing anything.
5. It then gets the cache key for the document's indexing status.
6. Inside a try-except block, it gets the dataset associated with the document, and if the document has no dataset, it raises an exception.
7. It then gets the appropriate index processor for the document's format and fetches all the segments associated with the document.
8. If there are any index node IDs, it cleans them from the index using the index processor.
9. If any exceptions occur during the process, it logs the exception and re-enables the document if it's not archived.
10. Finally, it deletes the indexing cache key.
11. The `remove_document_from_index_task` is a Celery task that calls the `remove_document_from_index` function asynchronously.
```


### import Relationships

Imports found:
import logging
import time
import click
from celery import shared_task
from werkzeug.exceptions import NotFound
from core.rag.index_processor.index_processor_factory import IndexProcessorFactory
from extensions.ext_database import db
from extensions.ext_redis import redis_client
from models.dataset import Document, DocumentSegment