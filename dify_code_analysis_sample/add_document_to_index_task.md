

### Summary

The code you provided is an asynchronous task for adding a document to an index. Here's a summary of the key elements:

1. **add_document_to_index_task**: This is a Celery shared task that is responsible for the asynchronous processing of adding a document to an index. It takes a `dataset_document_id` as a parameter.

2. **Workflow**:
   - It retrieves the `DatasetDocument` object from the database based on the `dataset_document_id`.
   - If the `indexing_status` of the `DatasetDocument` is not "completed", the task returns without doing anything.
   - It creates an indexing cache key in Redis to track the indexing process.
   - It retrieves all the `DocumentSegment` objects associated with the `DatasetDocument` and creates a list of `Document` objects from the segment contents.
   - It loads the documents into the index processor, which is determined by the `doc_form` field of the dataset associated with the `DatasetDocument`.
   - If any exceptions occur during the process, it updates the `DatasetDocument` object with the error information and disables the document.
   - Finally, it deletes the indexing cache key from Redis.

3. **Dependencies**:
   - The task uses several external libraries and modules, including `click`, `celery`, `werkzeug`, `core.rag.index_processor.index_processor_factory`, `core.rag.models.document`, `extensions.ext_database`, `extensions.ext_redis`, `models.dataset`, and `models.dataset`.
   - It interacts with the database and Redis to retrieve and update data.

Overall, this code is responsible for the asynchronous processing of adding a document to an index, handling potential errors, and updating the database and Redis accordingly.

### Highlights

The key features of this code are:

1. **Asynchronous Task**: The code uses Celery's `@shared_task` decorator to define an asynchronous task called `add_document_to_index_task`. This allows the task to be executed in the background, independent of the main application flow.

2. **Database Operations**: The code interacts with the database using SQLAlchemy, querying the `DatasetDocument` and `DocumentSegment` models to retrieve the necessary data for indexing.

3. **Document Indexing**: The code uses the `IndexProcessorFactory` to initialize an appropriate index processor based on the dataset's `doc_form` attribute. The documents are then loaded into the index.

4. **Error Handling**: The code includes error handling, where if an exception occurs during the indexing process, the `DatasetDocument` is marked as disabled and the error is logged.

5. **Caching**: The code uses a Redis cache key to track the indexing status of the document, and this key is deleted after the indexing is complete.

The overall purpose of this code is to asynchronously add a document to a search index, with error handling and caching mechanisms in place to ensure reliable and efficient indexing.```python
Here is the high-level pythonic pseudocode for the `add_document_to_index_task` function:

```python
# Define a Celery shared task to add a document to the index asynchronously
@shared_task(queue='dataset')
def add_document_to_index_task(dataset_document_id: str):
    """
    Asynchronously add a document to the index.

    Args:
        dataset_document_id (str): The ID of the dataset document to be added to the index.

    Usage:
        add_document_to_index.delay(document_id)
    """
    # Log the start of the task and record the start time
    logging.info(f"Start adding document to index: {dataset_document_id}")
    start_at = time.perf_counter()

    # Fetch the dataset document from the database
    dataset_document = db.session.query(DatasetDocument).filter(DatasetDocument.id == dataset_document_id).first()
    if not dataset_document:
        # Raise an exception if the document is not found
        raise NotFound("Document not found")

    # Check if the document is ready to be indexed
    if dataset_document.indexing_status != "completed":
        return

    # Get the indexing cache key for the document
    indexing_cache_key = f"document_{dataset_document.id}_indexing"

    try:
        # Fetch all the enabled segments of the document from the database
        segments = db.session.query(DocumentSegment).filter(
            DocumentSegment.document_id == dataset_document.id,
            DocumentSegment.enabled == True
        ).order_by(DocumentSegment.position.asc()).all()

        # Create a list of document objects from the segments
        documents = []
        for segment in segments:
            document = Document(
                page_content=segment.content,
                metadata={
                    "doc_id": segment.index_node_id,
                    "doc_hash": segment.index_node_hash,
                    "document_id": segment.document_id,
                    "dataset_id": segment.dataset_id,
                }
            )
            documents.append(document)

        # Fetch the dataset associated with the document
        dataset = dataset_document.dataset
        if not dataset:
            # Raise an exception if the document has no associated dataset
            raise Exception("Document has no dataset")

        # Get the index type from the dataset
        index_type = dataset.doc_form

        # Create an index processor based on the index type
        index_processor = IndexProcessorFactory(index_type).init_index_processor()

        # Load the documents into the index
        index_processor.load(dataset, documents)

        # Log the completion of the task and the latency
        end_at = time.perf_counter()
        logging.info(
            f"Document added to index: {dataset_document.id} latency: {end_at - start_at}"
        )
    except Exception as e:
        # Log the exception and update the document status
        logging.exception("add document to index failed")
        dataset_document.enabled = False
        dataset_document.disabled_at = datetime.datetime.utcnow()
        dataset_document.status = "error"
        dataset_document.error = str(e)
        db.session.commit()
    finally:
        # Delete the indexing cache key
        redis_client.delete(indexing_cache_key)
```

This high-level pseudocode provides a clear and concise overview of the logic implemented in the `add_document_to_index_task` function. It includes comments that explain the purpose of each section of the code, making it easy for developers to understand the overall flow of the function.

The pseudocode follows Python conventions and best practices, such as using descriptive variable names, handling exceptions, and logging relevant information. It also demonstrates the use of Celery shared tasks, database queries, and index processing, which are common components in a production-ready application.
```


### import Relationships

Imports found:
import datetime
import logging
import time
import click
from celery import shared_task
from werkzeug.exceptions import NotFound
from core.rag.index_processor.index_processor_factory import IndexProcessorFactory
from core.rag.models.document import Document
from extensions.ext_database import db
from extensions.ext_redis import redis_client
from models.dataset import Document as DatasetDocument
from models.dataset import DocumentSegment