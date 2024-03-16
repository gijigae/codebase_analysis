

### Summary

This Python file `batch_import_annotations_task.py` contains a Celery task called `batch_import_annotations_task` that is responsible for importing a batch of annotations into the system.

The key components of the codebase are:

1. **Celery Task**: The `batch_import_annotations_task` function is decorated with `@shared_task(queue='dataset')`, which means it is a Celery task that will be executed in the 'dataset' queue.

2. **Annotation Import**: The task takes the following parameters: `job_id`, `content_list` (a list of dictionaries containing the annotation data), `app_id`, `tenant_id`, and `user_id`. It then processes the `content_list` by creating `MessageAnnotation` objects and `Document` objects for each annotation, and adding them to the database.

3. **Indexing**: If the app's `AppAnnotationSetting` is configured to have annotation indexing enabled, the task will use the `DatasetCollectionBindingService` to get the appropriate `Dataset` object, and then use the `Vector` class to create the index for the new annotations.

4. **Caching and Error Handling**: The task uses Redis to cache the status of the import job, setting a key with a 600-second expiration time. If an error occurs during the import, the task will roll back the database transaction, set an error status in Redis, and log the error message.

Overall, this file is responsible for the batch import of annotations into the system, including creating the necessary database records and indexing the annotations for search and retrieval.

### Highlights

The key features in this code are:

1. **Celery Task**: The code defines a Celery shared task called `batch_import_annotations_task` that is responsible for importing a batch of annotations.

2. **Database Operations**: The code performs various database operations, including querying for an `App` instance, creating `MessageAnnotation` and `Document` instances, and committing the changes to the database.

3. **Indexing Annotations**: If the `AppAnnotationSetting` is enabled, the code creates a `Dataset` instance and uses the `Vector` class to index the annotations in the dataset.

4. **Caching and Error Handling**: The code uses Redis to cache the status of the job and the error messages in case of any exceptions.

5. **Logging**: The code extensively uses logging to provide information about the task execution, including the start and end times, and any errors that may occur.

Overall, the key feature of this code is the ability to import a batch of annotations, associate them with the appropriate `App` instance, and index them for search and retrieval purposes, with proper error handling and caching mechanisms.```python
Sure, here's the high-level pythonic pseudocode for the given code:

```python
# Define a Celery task to handle batch import of annotations
@shared_task(queue='dataset')
def batch_import_annotations_task(job_id, content_list, app_id, tenant_id, user_id):
    # Log the start of the task
    logging.info(f'Start batch import annotation: {job_id}')
    start_time = time.perf_counter()

    # Set a key in Redis to track the progress of the task
    indexing_cache_key = f'app_annotation_batch_import_{job_id}'

    # Fetch the app information from the database
    app = db.session.query(App).filter(
        App.id == app_id,
        App.tenant_id == tenant_id,
        App.status == 'normal'
    ).first()

    if app:
        try:
            # Create a list of Document objects from the content list
            documents = []
            for content in content_list:
                # Create a MessageAnnotation object and add it to the database
                annotation = MessageAnnotation(
                    app_id=app.id,
                    content=content['answer'],
                    question=content['question'],
                    account_id=user_id
                )
                db.session.add(annotation)
                db.session.flush()

                # Create a Document object with the annotation metadata
                document = Document(
                    page_content=content['question'],
                    metadata={
                        "annotation_id": annotation.id,
                        "app_id": app_id,
                        "doc_id": annotation.id
                    }
                )
                documents.append(document)

            # Check if annotation reply is enabled, and if so, batch add the annotations to the index
            app_annotation_setting = db.session.query(AppAnnotationSetting).filter(
                AppAnnotationSetting.app_id == app_id
            ).first()

            if app_annotation_setting:
                # Fetch the dataset collection binding for annotations
                dataset_collection_binding = DatasetCollectionBindingService.get_dataset_collection_binding_by_id_and_type(
                    app_annotation_setting.collection_binding_id,
                    'annotation'
                )
                if not dataset_collection_binding:
                    raise NotFound("App annotation setting not found")

                # Create a new Dataset object and index the documents
                dataset = Dataset(
                    id=app_id,
                    tenant_id=tenant_id,
                    indexing_technique='high_quality',
                    embedding_model_provider=dataset_collection_binding.provider_name,
                    embedding_model=dataset_collection_binding.model_name,
                    collection_binding_id=dataset_collection_binding.id
                )
                vector = Vector(dataset, attributes=['doc_id', 'annotation_id', 'app_id'])
                vector.create(documents, duplicate_check=True)

            # Commit the database changes and set the Redis key to indicate task completion
            db.session.commit()
            redis_client.setex(indexing_cache_key, 600, 'completed')
            end_time = time.perf_counter()
            logging.info(f'Build index successful for batch import annotation: {job_id} latency: {end_time - start_time}')
        except Exception as e:
            # Roll back the database changes and set the Redis key to indicate an error
            db.session.rollback()
            redis_client.setex(indexing_cache_key, 600, 'error')
            indexing_error_msg_key = f'app_annotation_batch_import_error_msg_{job_id}'
            redis_client.setex(indexing_error_msg_key, 600, str(e))
            logging.exception("Build index for batch import annotations failed")
```

This pseudocode covers the following high-level logic:

1. The `batch_import_annotations_task` function is defined as a Celery task, which will be executed in the `dataset` queue.
2. The function logs the start of the task and records the start time.
3. It sets a Redis key to track the progress of the task.
4. It fetches the app information from the database based on the provided `app_id` and `tenant_id`.
5. If the app is found, it creates MessageAnnotation and Document objects from the provided content list, and adds them to the database.
6. It checks if annotation reply is enabled for the app, and if so, it fetches the dataset collection binding for annotations.
7. If the dataset collection binding is found, it creates a new Dataset object and indexes the documents using the Vector class.
8. After the database changes are committed, it sets the Redis key to indicate the task completion.
9. If any exceptions occur during the process, it rolls back the database changes, sets the Redis key to indicate an error, and logs the exception.

This pseudocode provides a high-level overview of the task's functionality, including database and Redis operations, error handling, and logging. The actual implementation may include additional details and optimizations specific to the project requirements.
```


### import Relationships

Imports found:
import logging
import time
import click
from celery import shared_task
from werkzeug.exceptions import NotFound
from core.rag.datasource.vdb.vector_factory import Vector
from core.rag.models.document import Document
from extensions.ext_database import db
from extensions.ext_redis import redis_client
from models.dataset import Dataset
from models.model import App, AppAnnotationSetting, MessageAnnotation
from services.dataset_service import DatasetCollectionBindingService