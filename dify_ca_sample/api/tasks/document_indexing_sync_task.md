

### Summary

The codebase in the provided Python file `document_indexing_sync_task.py` is responsible for asynchronously updating and indexing documents in a document indexing system. Here's a summary of the key components and functionality:

1. **Async Task**: The codebase defines a Celery shared task named `document_indexing_sync_task`. This task is responsible for handling the asynchronous update and indexing of documents.

2. **Document Retrieval**: The task retrieves a document from the database based on the provided `dataset_id` and `document_id`. If the document is not found, a `NotFound` exception is raised.

3. **Notion Extractor**: If the document's data source type is "notion_import", the task uses the `NotionExtractor` to retrieve the latest content and metadata of the Notion page associated with the document. It checks if the page has been updated since the last indexing.

4. **Index Cleanup**: If the page has been updated, the task deletes all existing document segments and the associated index entries from the vector index.

5. **Indexing**: After the cleanup, the task triggers the `IndexingRunner` to re-index the document and update the index.

6. **Error Handling**: The task includes exception handling for various scenarios, such as when the document is paused or the indexing process fails.

7. **Logging**: The task uses the `logging` module to log relevant information, such as the start and end of the indexing process, the latency, and any errors that occur.

In summary, this codebase is responsible for efficiently updating and re-indexing documents in a document indexing system, specifically handling the case of Notion-imported documents. It ensures that the document index is kept up-to-date with the latest changes in the source data.

### Highlights

The key features of this code are:

1. **Asynchronous Task Execution**: The code uses Celery's `@shared_task` decorator to define an asynchronous task, `document_indexing_sync_task`, which can be executed in the background.

2. **Document Indexing and Updating**: The main purpose of the code is to handle the indexing and updating of documents. It fetches the document from the database, checks if the data source has been updated, and then proceeds to update the document's indexing status and process the document through the `IndexingRunner`.

3. **Notion Integration**: The code handles the case where the document is associated with a Notion page. It extracts the necessary information from the Notion data source and updates the document accordingly.

4. **Error Handling**: The code includes error handling for various scenarios, such as when the document or dataset is not found, or when there are issues during the indexing process.

5. **Logging and Timing**: The code includes logging statements to provide information about the task execution, and measures the time taken to perform various operations.

The key focus of this code is to ensure that documents are properly indexed and updated based on changes in their data sources, with a particular emphasis on integrating with Notion as a data source.```python
Sure, here's the high-level pythonic pseudocode for the given code:

```python
# Function to handle document indexing and synchronization
@shared_task(queue='dataset')
def document_indexing_sync_task(dataset_id: str, document_id: str):
    """
    Asynchronously updates a document in the system.

    Args:
        dataset_id (str): The ID of the dataset the document belongs to.
        document_id (str): The ID of the document to be updated.
    """
    # Log the start of the task
    logging.info(f"Start sync document: {document_id}")
    start_time = time.perf_counter()

    # Fetch the document from the database
    document = get_document(dataset_id, document_id)

    # Check if the document exists
    if not document:
        raise NotFound("Document not found")

    # Determine the data source type and extract relevant information
    data_source_type = document.data_source_type
    data_source_info = document.data_source_info_dict

    # Handle Notion-based documents
    if data_source_type == 'notion_import':
        handle_notion_document(document, data_source_info)

# Helper function to handle Notion-based documents
def handle_notion_document(document, data_source_info):
    # Extract Notion-specific information from the data source info
    workspace_id = data_source_info['notion_workspace_id']
    page_id = data_source_info['notion_page_id']
    page_type = data_source_info['type']
    page_edited_time = data_source_info['last_edited_time']

    # Fetch the data source binding for the Notion workspace
    data_source_binding = get_data_source_binding(document.tenant_id, workspace_id)

    # Create a Notion extractor and get the latest edited time
    loader = NotionExtractor(workspace_id, page_id, page_type, data_source_binding.access_token, document.tenant_id)
    last_edited_time = loader.get_notion_last_edited_time()

    # Check if the Notion page has been updated
    if last_edited_time != page_edited_time:
        # Update the document's indexing status and processing start time
        update_document_status(document, 'parsing')

        # Delete all document segments and index entries
        delete_document_segments_and_index(document.id, document.dataset_id, document.doc_form)

        # Reindex the document
        reindex_document(document)

# Helper function to fetch a document from the database
def get_document(dataset_id: str, document_id: str):
    return db.session.query(Document).filter(
        Document.id == document_id,
        Document.dataset_id == dataset_id
    ).first()

# Helper function to fetch a data source binding
def get_data_source_binding(tenant_id: str, workspace_id: str):
    return DataSourceBinding.query.filter(
        db.and_(
            DataSourceBinding.tenant_id == tenant_id,
            DataSourceBinding.provider == 'notion',
            DataSourceBinding.disabled == False,
            DataSourceBinding.source_info['workspace_id'] == f'"{workspace_id}"'
        )
    ).first()

# Helper function to update a document's indexing status
def update_document_status(document: Document, status: str):
    document.indexing_status = status
    document.processing_started_at = datetime.datetime.utcnow()
    db.session.commit()

# Helper function to delete document segments and index entries
def delete_document_segments_and_index(document_id: str, dataset_id: str, index_type: str):
    dataset = get_dataset(dataset_id)
    index_processor = IndexProcessorFactory(index_type).init_index_processor()

    segments = get_document_segments(document_id)
    index_node_ids = [segment.index_node_id for segment in segments]

    # Delete from the vector index
    index_processor.clean(dataset, index_node_ids)

    for segment in segments:
        db.session.delete(segment)

# Helper function to reindex a document
def reindex_document(document: Document):
    indexing_runner = IndexingRunner()
    indexing_runner.run([document])
```

This pseudocode provides a high-level overview of the document indexing and synchronization task. It includes the main function `document_indexing_sync_task` and several helper functions to handle various aspects of the task, such as fetching the document, extracting Notion-specific information, updating the document status, deleting segments and index entries, and reindexing the document.

The pseudocode is written in a Pythonic style, using type annotations, docstrings, and descriptive variable and function names to make the code more readable and understandable.
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
from core.rag.extractor.notion_extractor import NotionExtractor
from core.rag.index_processor.index_processor_factory import IndexProcessorFactory
from extensions.ext_database import db
from models.dataset import Dataset, Document, DocumentSegment
from models.source import DataSourceBinding