

### Summary

This is a Python file called `clean_notion_document_task.py` that contains a Celery shared task function `clean_notion_document_task()`. This task is responsible for cleaning up documents and their associated data when a document is deleted from a dataset in Notion.

The main functionality of the code is as follows:

1. The `clean_notion_document_task()` function is a Celery shared task that is triggered when a document is deleted from a Notion dataset.
2. The function takes two parameters: `document_ids` (a list of document IDs to be cleaned up) and `dataset_id` (the ID of the dataset that the documents belong to).
3. The function first retrieves the dataset object from the database using the `dataset_id`.
4. It then initializes an `IndexProcessorFactory` object based on the `doc_form` field of the dataset, which determines the type of index used for the dataset.
5. For each document ID in the `document_ids` list, the function retrieves the corresponding `Document` object from the database and deletes it.
6. The function also retrieves all `DocumentSegment` objects associated with the deleted document and deletes them as well.
7. Additionally, the function calls the `clean()` method of the `IndexProcessor` object to remove the corresponding index nodes from the index.
8. Finally, the changes are committed to the database.

The code also includes error handling and logging to provide information about the task's execution, such as the dataset ID and the time taken to complete the task.

Overall, this code is part of a larger system that manages datasets and documents, and it is responsible for cleaning up the database and index when documents are deleted from a Notion dataset.

### Highlights

The key features of this code are:

1. **Task Definition**: The code defines a Celery shared task called `clean_notion_document_task` that is used to clean up documents and their associated data when a document is deleted from a dataset.

2. **Database Interactions**: The code interacts with the database using the `db.session` object to fetch the dataset, documents, and document segments, and to delete them from the database.

3. **Index Processor**: The code uses an `IndexProcessorFactory` to initialize an `IndexProcessor` based on the dataset's `doc_form` attribute. The `IndexProcessor` is then used to clean up the associated index data for the deleted documents.

4. **Error Handling**: The code wraps the main logic in a try-except block to handle any exceptions that may occur during the task execution.

5. **Logging and Timing**: The code logs the start and end of the task execution, along with the latency, using the `logging` and `click.style` functions.

Overall, the key feature of this code is the ability to efficiently clean up documents, their associated data, and the corresponding index data when a document is deleted from a dataset, as part of an asynchronous task in a Celery-based system.```python
Here's the high-level pythonic pseudocode for the `clean_notion_document_task` function:

```python
# Define a Celery shared task for cleaning Notion documents
@shared_task(queue='dataset')
def clean_notion_document_task(document_ids: list[str], dataset_id: str):
    """
    Clean document when document deleted from Notion.
    
    Args:
        document_ids (list[str]): List of document IDs to be cleaned.
        dataset_id (str): ID of the dataset associated with the documents.
    """
    # Log the start of the task
    logging.info(f"Start cleaning documents when imported from Notion: {dataset_id}")
    start_time = time.perf_counter()

    try:
        # Fetch the dataset associated with the documents
        dataset = db.session.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise Exception("Document has no dataset")

        # Get the index processor based on the document form
        index_type = dataset.doc_form
        index_processor = IndexProcessorFactory(index_type).init_index_processor()

        # Clean each document and its associated segments
        for document_id in document_ids:
            # Delete the document
            document = db.session.query(Document).filter(Document.id == document_id).first()
            db.session.delete(document)

            # Delete the associated segments and clean the index
            segments = db.session.query(DocumentSegment).filter(DocumentSegment.document_id == document_id).all()
            index_node_ids = [segment.index_node_id for segment in segments]
            index_processor.clean(dataset, index_node_ids)

            # Delete the segments
            for segment in segments:
                db.session.delete(segment)

        # Commit the database changes
        db.session.commit()

        # Log the completion of the task and the elapsed time
        end_time = time.perf_counter()
        logging.info(f"Cleaned documents when imported from Notion: {dataset_id} | Latency: {end_time - start_time}")
    except Exception:
        # Log the failure of the task
        logging.exception("Cleaning documents when imported from Notion failed")
```

In this pseudocode, the `clean_notion_document_task` function is defined as a Celery shared task, which means it can be executed asynchronously in the background. The function takes a list of document IDs and a dataset ID as input.

The function first logs the start of the task and the current time. It then fetches the dataset associated with the given dataset ID. If no dataset is found, an exception is raised.

Next, the function initializes the appropriate index processor based on the document form of the dataset. It then iterates through each document ID, deleting the corresponding document and its associated segments. For each segment, the function also cleans the index using the index processor.

After all the documents and segments have been deleted, the function commits the database changes and logs the completion of the task along with the elapsed time.

If any exceptions occur during the task execution, the function logs the failure.
```


### import Relationships

Imports found:
import logging
import time
import click
from celery import shared_task
from core.rag.index_processor.index_processor_factory import IndexProcessorFactory
from extensions.ext_database import db
from models.dataset import Dataset, Document, DocumentSegment