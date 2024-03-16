

### Summary

This Python file `document_indexing_update_task.py` contains a Celery task function called `document_indexing_update_task` that is responsible for updating a document's indexing status in a database-backed application.

Here's a summary of the code:

1. The task function `document_indexing_update_task` is a shared Celery task that runs in the 'dataset' queue.
2. The task takes two parameters: `dataset_id` and `document_id`.
3. The function first retrieves the `Document` instance from the database based on the `dataset_id` and `document_id`.
4. If the document is not found, it raises a `NotFound` exception.
5. The function then updates the `indexing_status` and `processing_started_at` fields of the `Document` instance.
6. It then deletes all the related `DocumentSegment` instances and removes the corresponding index entries from the index processor.
7. Finally, it creates an `IndexingRunner` instance and runs the indexing process for the updated document.
8. The task handles exceptions, such as `DocumentIsPausedException` and other general exceptions, and logs the relevant information.

Overall, this task is responsible for updating the indexing status of a document, deleting the existing index data, and re-indexing the document. This is likely part of a larger document indexing and search system.

### Highlights

The key features of this code are:

1. **Celery Task**: The code defines a Celery shared task called `document_indexing_update_task` that is used to asynchronously update a document.

2. **Database Operations**: The code interacts with the database using SQLAlchemy to fetch and update the `Document`, `Dataset`, and `DocumentSegment` models.

3. **Index Cleanup**: When updating a document, the code first deletes all the existing document segments and their associated index nodes from the vector index using the `IndexProcessorFactory` and `IndexingRunner`.

4. **Indexing Execution**: After cleaning up the old index, the code triggers the indexing process for the updated document using the `IndexingRunner`.

5. **Error Handling**: The code handles various exceptions that may occur during the indexing process, such as `NotFound` (document not found), `DocumentIsPausedException`, and any other general exceptions.

The key purpose of this code is to provide an asynchronous task that can update the indexing of a document in the system, handling the necessary cleanup and re-indexing steps.```python
Here's the high-level pythonic pseudocode for the given code:

```python
# Define a Celery task for asynchronous document indexing update
@shared_task(queue='dataset')
def document_indexing_update_task(dataset_id, document_id):
    """
    Asynchronously update a document in the indexing process.

    Args:
        dataset_id (str): The ID of the dataset containing the document.
        document_id (str): The ID of the document to be updated.
    """
    # Log the start of the document update process
    logging.info(f'Start update document: {document_id}')
    start_time = time.perf_counter()

    # Fetch the document from the database
    document = db.session.query(Document).filter(
        Document.id == document_id,
        Document.dataset_id == dataset_id
    ).first()

    # If the document is not found, raise a NotFound exception
    if not document:
        raise NotFound('Document not found')

    # Update the document's indexing status and processing start time
    document.indexing_status = 'parsing'
    document.processing_started_at = datetime.datetime.utcnow()
    db.session.commit()

    try:
        # Fetch the dataset associated with the document
        dataset = db.session.query(Dataset).filter(Dataset.id == dataset_id).first()
        if not dataset:
            raise Exception('Dataset not found')

        # Get the index processor based on the document's form
        index_type = document.doc_form
        index_processor = IndexProcessorFactory(index_type).init_index_processor()

        # Fetch all the document segments and their index node IDs
        segments = db.session.query(DocumentSegment).filter(DocumentSegment.document_id == document_id).all()
        index_node_ids = [segment.index_node_id for segment in segments]

        # Delete the document segments and their index entries
        index_processor.clean(dataset, index_node_ids)
        for segment in segments:
            db.session.delete(segment)
        db.session.commit()
        end_time = time.perf_counter()
        logging.info(f'Cleaned document when document update data source or process rule: {document_id} latency: {end_time - start_time}')
    except Exception:
        logging.exception("Cleaned document when document update data source or process rule failed")

    try:
        # Run the indexing process for the updated document
        indexing_runner = IndexingRunner()
        indexing_runner.run([document])
        end_time = time.perf_counter()
        logging.info(f'Update document: {document.id} latency: {end_time - start_time}')
    except DocumentIsPausedException as ex:
        logging.info(f'{str(ex)}')
    except Exception:
        pass
```

This pseudocode outlines the high-level logic of the `document_indexing_update_task` function. It first logs the start of the document update process and fetches the document from the database. If the document is not found, it raises a `NotFound` exception.

Next, it updates the document's indexing status and processing start time, then proceeds to delete all the document segments and their corresponding index entries. This is done by fetching the dataset associated with the document, getting the appropriate index processor, and then cleaning the index.

Finally, it runs the indexing process for the updated document using the `IndexingRunner` class. If any exceptions occur during the process, they are caught and logged appropriately.

The pseudocode is designed to be abstract and informative, providing a high-level overview of the task's functionality without getting into the implementation details.
```


### import Relationships

Imports found:
import datetime
import logging
import time
import click
from celery import shared_task
from werkzeug.exceptions import NotFound
from core.indexing_runner import DocumentIsPausedException, IndexingRunner
from core.rag.index_processor.index_processor_factory import IndexProcessorFactory
from extensions.ext_database import db
from models.dataset import Dataset, Document, DocumentSegment