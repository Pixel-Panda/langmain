from typing import List, Optional

from langflow.components.vectorstores.base.model import LCVectorStoreComponent
from langflow.components.vectorstores.Couchbase import CouchbaseComponent
from langflow.field_typing import Embeddings, NestedDict, Text
from langflow.schema import Record


class CouchbaseSearchComponent(LCVectorStoreComponent):
    display_name = "Couchbase Search"
    description = "Search a Couchbase Vector Store for similar documents."
    documentation = "https://python.langchain.com/docs/integrations/vectorstores/couchbase"
    field_order = [
        "couchbase_connection_string",
        "couchbase_username",
        "couchbase_password",
        "bucket_name",
        "scope_name",
        "collection_name",
        "index_name",
    ]

    def build_config(self):
        return {
            "search_type": {
                "display_name": "Search Type",
                "options": ["Similarity", "MMR"],
            },
            "input_value": {"display_name": "Input"},
            "embedding": {"display_name": "Embedding"},
            "couchbase_connection_string": {"display_name": "Couchbase Cluster connection string"},
            "couchbase_username": {"display_name": "Couchbase username"},
            "couchbase_password": {
                "display_name": "Couchbase password",
                "password": True,
            },
            "bucket_name": {"display_name": "Bucket Name"},
            "scope_name": {"display_name": "Scope Name"},
            "collection_name": {"display_name": "Collection Name"},
            "index_name": {"display_name": "Index Name"},
            "search_kwargs": {"display_name": "Search Kwargs", "advanced": True},
            "number_of_results": {
                "display_name": "Number of Results",
                "info": "Number of results to return.",
                "advanced": True,
            },
        }

    def build(  # type: ignore[override]
        self,
        input_value: Text,
        search_type: str,
        embedding: Embeddings,
        number_of_results: int = 4,
        bucket_name: str = "",
        scope_name: str = "",
        collection_name: str = "",
        index_name: str = "",
        couchbase_connection_string: str = "",
        couchbase_username: str = "",
        couchbase_password: str = "",
        search_kwargs: Optional[NestedDict] = None,
    ) -> List[Record]:
        search_kwargs = search_kwargs or {}
        vector_store = CouchbaseComponent().build(
            couchbase_connection_string=couchbase_connection_string,
            couchbase_username=couchbase_username,
            couchbase_password=couchbase_password,
            bucket_name=bucket_name,
            scope_name=scope_name,
            collection_name=collection_name,
            embedding=embedding,
            index_name=index_name,
        )
        if not vector_store:
            raise ValueError("Failed to create Couchbase Vector Store")
        return self.search_with_vector_store(
            vector_store=vector_store, input_value=input_value, search_type=search_type, k=number_of_results
        )
