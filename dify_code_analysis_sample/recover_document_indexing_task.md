

### Summary

This Python file, `recover_document_indexing_task.py`, contains a single Celery task function named `recover_document_indexing_task`. This task is responsible for recovering the indexing process for a specific document in a dataset.

Here's a breakdown of the codebase:

1. **Imports**:
   - The file imports necessary modules and classes, such as `logging`, `time`, `click`, `celery`, `werkzeug.exceptions`, and various classes from the project's own modules.

2. **recover_document_indexing_task**:
   - This function is a Celery shared task, which means it can be called asynchronously by other parts of the application.
   - The task takes two parameters: `dataset_id` and `document_id`, which are used to retrieve the document from the database.
   - The function logs the start of the task and the document ID being processed.
   - It then retrieves the document from the database using the provided `dataset_id` and `document_id`.
   - If the document is not found, the function raises a `NotFound` exception.
   - Based on the current indexing status of the document, the function creates an instance of the `IndexingRunner` class and calls the appropriate method to continue the indexing process.
   - The function logs the time it took to process the document.
   - If a `DocumentIsPausedException` is raised, the function logs a yellow message. If any other exception occurs, the function simply passes.

In summary, this codebase provides a Celery task that can be used to recover the indexing process for a specific document in a dataset. The task retrieves the document from the database, checks its current indexing status, and then calls the appropriate method of the `IndexingRunner` class to continue the indexing process.

### Highlights

Here are the key features of the provided code:

1. **Asynchronous Task**: The code defines an asynchronous task using the `@shared_task` decorator from the Celery library. This allows the task to be executed in the background, independent of the main application.

2. **Document Recovery**: The primary purpose of the code is to recover the indexing process for a specific document. The `recover_document_indexing_task` function takes the `dataset_id` and `document_id` as parameters and attempts to resume the indexing process for the given document.

3. **Database Interaction**: The code interacts with the database using the `db.session.query(Document)` method to fetch the document based on the provided `document_id` and `dataset_id`.

4. **Indexing Runner**: The code utilizes the `IndexingRunner` class to handle the indexing process for the document. Depending on the current indexing status of the document, the appropriate method (`run`, `run_in_splitting_status`, or `run_in_indexing_status`) is called.

5. **Error Handling**: The code includes exception handling to handle specific scenarios, such as when the document is paused (`DocumentIsPausedException`) or when any other exception occurs.

The key feature of this code is the ability to recover the indexing process for a specific document, which can be useful in scenarios where the indexing process has been interrupted or paused for some reason.```python
Sure, here's the high-level pythonic pseudocode for the `recover_document_indexing_task` function:

```python
# Define a Celery task to be executed asynchronously
@shared_task(queue='dataset')
def recover_document_indexing_task(dataset_id: str, document_id: str):
    """
    Asynchronously recover a document's indexing process.

    Args:
        dataset_id (str): The ID of the dataset the document belongs to.
        document_id (str): The ID of the document to be recovered.
    """
    # Log the start of the task and record the start time
    logging.info(f"Recover document: {document_id}")
    start_time = time.perf_counter()

    # Fetch the document from the database
    document = fetch_document(dataset_id, document_id)

    # If the document is not found, raise a NotFound exception
    if not document:
        raise NotFound("Document not found")

    try:
        # Create an IndexingRunner instance
        indexing_runner = IndexingRunner()

        # Determine the appropriate indexing step based on the document's status
        if document.indexing_status in ["waiting", "parsing", "cleaning"]:
            indexing_runner.run([document])
        elif document.indexing_status == "splitting":
            indexing_runner.run_in_splitting_status(document)
        elif document.indexing_status == "indexing":
            indexing_runner.run_in_indexing_status(document)

        # Log the completion of the task and the processing time
        end_time = time.perf_counter()
        logging.info(f"Processed document: {document.id} | Latency: {end_time - start_time}")
    except DocumentIsPausedException as ex:
        # Log the exception if the document is paused
        logging.info(click.style(str(ex), fg='yellow'))
    except Exception:
        # Log any other exceptions that may occur
        pass
```

Here's a breakdown of the high-level pseudocode:

1. The function is defined as a Celery task, which allows it to be executed asynchronously.
2. The function takes two arguments: `dataset_id` and `document_id`, which are used to identify the document to be recovered.
3. The function logs the start of the task and records the start time.
4. The function fetches the document from the database using the provided `dataset_id` and `document_id`.
5. If the document is not found, the function raises a `NotFound` exception.
6. The function creates an `IndexingRunner` instance, which is responsible for managing the document indexing process.
7. Based on the document's current indexing status, the function calls the appropriate method on the `IndexingRunner` instance to resume the indexing process.
8. The function logs the completion of the task and the total processing time.
9. If a `DocumentIsPausedException` is raised, the function logs the exception.
10. If any other exception is raised, the function logs the exception.

The key aspects of this pseudocode are:
- Asynchronous task execution using Celery
- Fetching the document from the database
- Handling different document indexing statuses
- Logging the task progress and any exceptions

This high-level pseudocode provides a clear overview of the functionality and structure of the `recover_document_indexing_task` function, without delving into the implementation details.
```


### import Relationships

Imports found:
import logging
import time
import click
from celery import shared_task
from werkzeug.exceptions import NotFound
from core.indexing_runner import DocumentIsPausedException, IndexingRunner
from extensions.ext_database import db
from models.dataset import Document