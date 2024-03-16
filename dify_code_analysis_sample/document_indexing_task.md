

### Summary

This Python file `document_indexing_task.py` is responsible for handling the asynchronous document indexing process within a codebase. Here's an overall summary of the codebase:

1. **Imports**: The file imports various modules and classes, including `datetime`, `logging`, `time`, `click`, `celery`, `flask`, `indexing_runner`, `ext_database`, `models`, and `services`.

2. **`document_indexing_task` function**: This function is a Celery shared task that runs asynchronously. It takes a `dataset_id` and a list of `document_ids` as input parameters. The main functionality of this task is as follows:
   - Retrieves the dataset and the associated features based on the given `dataset_id`.
   - Checks the document limit based on the features and the current app's configuration. If the limit is exceeded, it marks the documents as having an error and returns.
   - Retrieves the documents from the database based on the `document_ids` and updates their indexing status to 'parsing'.
   - Creates an `IndexingRunner` instance and runs the indexing process for the retrieved documents.
   - Logs the processing time for the dataset.
   - Handles exceptions, such as `DocumentIsPausedException`, and updates the document status accordingly.

3. **Usage**: The `document_indexing_task` function is meant to be called asynchronously, for example, using `document_indexing_task.delay(dataset_id, document_id)`.

4. **Dependencies**: The codebase relies on several external libraries and services, including Celery, Flask, the database layer (`ext_database` and `models`), and the `FeatureService` from the `services` module.

5. **Error Handling**: The codebase handles various exceptions, such as `DocumentIsPausedException` and general exceptions, and updates the document status accordingly.

Overall, this codebase is responsible for the asynchronous indexing of documents within a dataset, with considerations for document limits and error handling.

### Highlights

Here are the key features of the provided code:

1. **Asynchronous Task**: The code defines a Celery shared task called `document_indexing_task` that is responsible for processing documents asynchronously.

2. **Database Interactions**: The code interacts with the database using the `db` object from the `extensions.ext_database` module. It queries the `Dataset` and `Document` models to fetch data and update the indexing status of documents.

3. **Feature Checks**: The code checks the features of the dataset's tenant, specifically the `billing.enabled` and `vector_space.limit` settings, to ensure that the number of documents to be indexed does not exceed the limits.

4. **Document Indexing**: The code creates an `IndexingRunner` instance and calls its `run` method to perform the actual indexing of the documents.

5. **Error Handling**: The code catches exceptions, such as `DocumentIsPausedException`, and updates the indexing status and error message of the documents accordingly.

Overall, the key focus of this code is to handle the asynchronous indexing of documents, while ensuring that the indexing process adheres to the tenant's feature limitations and properly handles any errors that may occur during the indexing process.```python
Here's the high-level pythonic pseudocode for the provided code:

```python
# Import necessary modules and dependencies
import datetime
import logging
import time
import click
from celery import shared_task
from flask import current_app
from core.indexing_runner import DocumentIsPausedException, IndexingRunner
from extensions.ext_database import db
from models.dataset import Dataset, Document
from services.feature_service import FeatureService

# Define the document_indexing_task function as a Celery shared task
@shared_task(queue='dataset')
def document_indexing_task(dataset_id: str, document_ids: list):
    """
    Asynchronously process documents for a given dataset.

    Args:
        dataset_id (str): The ID of the dataset.
        document_ids (list): A list of document IDs to be processed.
    """
    # Initialize a list to store the documents
    documents = []

    # Record the start time of the task
    start_at = time.perf_counter()

    # Fetch the dataset from the database
    dataset = db.session.query(Dataset).filter(Dataset.id == dataset_id).first()

    # Check the document limit based on the dataset's tenant features
    try:
        features = FeatureService.get_features(dataset.tenant_id)
        if features.billing.enabled:
            vector_space = features.vector_space
            count = len(document_ids)
            batch_upload_limit = int(current_app.config['BATCH_UPLOAD_LIMIT'])
            if count > batch_upload_limit:
                raise ValueError(f"You have reached the batch upload limit of {batch_upload_limit}.")
            if 0 < vector_space.limit <= vector_space.size:
                raise ValueError("Your total number of documents plus the number of uploads have over the limit of your subscription.")
    except Exception as e:
        # Handle the error by updating the indexing status and error message for each document
        for document_id in document_ids:
            document = db.session.query(Document).filter(
                Document.id == document_id,
                Document.dataset_id == dataset_id
            ).first()
            if document:
                document.indexing_status = 'error'
                document.error = str(e)
                document.stopped_at = datetime.datetime.utcnow()
                db.session.add(document)
        db.session.commit()
        return

    # Fetch the documents from the database and update their indexing status
    for document_id in document_ids:
        logging.info(click.style(f'Start process document: {document_id}', fg='green'))
        document = db.session.query(Document).filter(
            Document.id == document_id,
            Document.dataset_id == dataset_id
        ).first()
        if document:
            document.indexing_status = 'parsing'
            document.processing_started_at = datetime.datetime.utcnow()
            documents.append(document)
            db.session.add(document)
    db.session.commit()

    # Process the documents using the IndexingRunner
    try:
        indexing_runner = IndexingRunner()
        indexing_runner.run(documents)
        end_at = time.perf_counter()
        logging.info(click.style(f'Processed dataset: {dataset_id} latency: {end_at - start_at}', fg='green'))
    except DocumentIsPausedException as ex:
        logging.info(click.style(str(ex), fg='yellow'))
    except Exception:
        pass
```

The key aspects of this pseudocode are:

1. The `document_indexing_task` function is defined as a Celery shared task, which allows it to be executed asynchronously.
2. The function takes a `dataset_id` and a list of `document_ids` as input.
3. It fetches the dataset from the database and checks the document limit based on the dataset's tenant features.
4. If the document limit is exceeded, it updates the indexing status and error message for each document and returns.
5. Otherwise, it fetches the documents from the database, updates their indexing status, and appends them to the `documents` list.
6. The `IndexingRunner` is then used to process the documents.
7. If a `DocumentIsPausedException` is raised, it is logged with a yellow color. Any other exceptions are caught and ignored.
8. The total processing time is logged with a green color.

The pseudocode provides a high-level overview of the functionality without getting into the implementation details of each step. It highlights the key responsibilities of the `document_indexing_task` function, such as fetching the dataset, checking the document limit, updating the indexing status, and processing the documents using the `IndexingRunner`.
```


### import Relationships

Imports found:
import datetime
import logging
import time
import click
from celery import shared_task
from flask import current_app
from core.indexing_runner import DocumentIsPausedException, IndexingRunner
from extensions.ext_database import db
from models.dataset import Dataset, Document
from services.feature_service import FeatureService