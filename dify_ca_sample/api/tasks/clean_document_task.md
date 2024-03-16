

### Summary

The provided code is a Python file named `clean_document_task.py` that contains a Celery task called `clean_document_task`. This task is responsible for cleaning up document data when a document is deleted.

Here's a summary of the code:

1. Imports:
   - `logging` and `time` for logging and timing the task execution.
   - `click` for providing colored console output.
   - `celery` for using the `shared_task` decorator to define a Celery task.
   - `IndexProcessorFactory` from `core.rag.index_processor.index_processor_factory` for initializing an index processor.
   - `db` from `extensions.ext_database` for interacting with the database.
   - `Dataset` and `DocumentSegment` from `models.dataset` for database models.

2. The `clean_document_task` function is a Celery task that takes three parameters:
   - `document_id`: The ID of the document to be cleaned up.
   - `dataset_id`: The ID of the dataset the document belongs to.
   - `doc_form`: The form of the document.

3. The task performs the following actions:
   - Retrieves the `Dataset` object for the given `dataset_id`.
   - Retrieves all `DocumentSegment` objects associated with the `document_id`.
   - If there are any `DocumentSegment` objects, it initializes an `IndexProcessor` using the `IndexProcessorFactory` and the `doc_form`.
   - The `IndexProcessor` is used to clean up the index data for the associated `index_node_ids` from the `DocumentSegment` objects.
   - The `DocumentSegment` objects are then deleted from the database.
   - The changes are committed to the database.
   - Logging is used to report the successful completion of the task and the latency.

4. If any exceptions occur during the task execution, they are caught, and an error message is logged.

In summary, the `clean_document_task` is a Celery task that is responsible for cleaning up document data, including removing any associated index data and deleting the document segments, when a document is deleted.

### Highlights

The key features of this code are:

1. **Task Definition**: This code defines a Celery task called `clean_document_task` using the `@shared_task` decorator. Celery is a distributed task queue system that allows you to run tasks asynchronously.

2. **Database Operations**: The code interacts with the database using the `db` object from the `extensions.ext_database` module. It retrieves a `Dataset` object, and then queries and deletes `DocumentSegment` objects related to the specified `document_id`.

3. **Index Processor**: The code uses the `IndexProcessorFactory` to create an `IndexProcessor` object, which is then used to clean the index entries associated with the deleted document segments.

4. **Logging and Exception Handling**: The code uses the `logging` module to log information about the task execution, including the start and end times. It also includes exception handling to log any errors that occur during the task execution.

5. **Usage Example**: The code includes a comment that provides an example of how to use the `clean_document_task` function, which is to call the `delay()` method and pass the `document_id` and `dataset_id` as arguments.

Overall, this code is responsible for cleaning up the database and index entries associated with a deleted document, which is a common task in document-based applications.```python
Here's the high-level pythonic pseudocode for the `clean_document_task` function:

```python
# Define a Celery task function to clean up documents when they are deleted
@shared_task(queue='dataset')
def clean_document_task(document_id: str, dataset_id: str, doc_form: str):
    """
    Clean up document-related data when a document is deleted.

    Args:
        document_id (str): The ID of the document to be cleaned up.
        dataset_id (str): The ID of the dataset the document belongs to.
        doc_form (str): The form of the document.
    """
    # Log the start of the task
    logging.info(click.style(f'Start clean document when document deleted: {document_id}', fg='green'))
    start_at = time.perf_counter()

    try:
        # Fetch the dataset the document belongs to
        dataset = db.session.query(Dataset).filter(Dataset.id == dataset_id).first()

        # Raise an exception if the document has no dataset
        if not dataset:
            raise Exception('Document has no dataset')

        # Fetch all the segments associated with the document
        segments = db.session.query(DocumentSegment).filter(DocumentSegment.document_id == document_id).all()

        # If there are any segments, clean up the associated index nodes
        if segments:
            index_node_ids = [segment.index_node_id for segment in segments]
            index_processor = IndexProcessorFactory(doc_form).init_index_processor()
            index_processor.clean(dataset, index_node_ids)

            # Delete all the segments associated with the document
            for segment in segments:
                db.session.delete(segment)

            # Commit the database changes
            db.session.commit()

        # Log the successful completion of the task
        end_at = time.perf_counter()
        logging.info(
            click.style(f'Cleaned document when document deleted: {document_id} latency: {end_at - start_at}', fg='green'))
    except Exception:
        # Log the failure of the task
        logging.exception("Cleaned document when document deleted failed")
```

The key points of this pseudocode are:

1. The function is defined as a Celery task, which allows it to be executed asynchronously in the background.
2. The function takes three parameters: the ID of the document to be cleaned up, the ID of the dataset the document belongs to, and the form of the document.
3. The function first logs the start of the task and records the start time.
4. It then fetches the dataset the document belongs to, and raises an exception if the document has no dataset.
5. It fetches all the segments associated with the document, and if there are any, it cleans up the associated index nodes using the `IndexProcessorFactory` and deletes all the segments.
6. The database changes are then committed.
7. The function logs the successful completion of the task and the time it took to execute.
8. If any exceptions occur during the task, the function logs the failure.

This pseudocode provides a high-level overview of the logic behind the `clean_document_task` function, without getting into the specific implementation details.
```


### import Relationships

Imports found:
import logging
import time
import click
from celery import shared_task
from core.rag.index_processor.index_processor_factory import IndexProcessorFactory
from extensions.ext_database import db
from models.dataset import Dataset, DocumentSegment