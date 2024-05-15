from typing import List, Optional, Union

from langchain.schema import BaseRetriever

from langchain_community.vectorstores import CouchbaseVectorStore

from langflow.custom import CustomComponent
from langflow.field_typing import Embeddings, VectorStore
from langflow.schema import Record

from datetime import timedelta

from couchbase.auth import PasswordAuthenticator
from couchbase.cluster import Cluster
from couchbase.options import ClusterOptions


class CouchbaseComponent(CustomComponent):
    display_name = "Couchbase"
    description = "Construct a `Couchbase Vector Search` vector store from raw documents."
    documentation = "https://python.langchain.com/docs/integrations/vectorstores/couchbase"
    icon = "Couchbase"
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
            "inputs": {"display_name": "Input", "input_types": ["Document", "Record"]},
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
        }

    def build(
        self,
        embedding: Embeddings,
        inputs: Optional[List[Record]] = None,
        bucket_name: str = "",
        scope_name: str = "",
        collection_name: str = "",
        index_name: str = "",
        couchbase_connection_string: str = "",
        couchbase_username: str = "",
        couchbase_password: str = "",
    ) -> Union[VectorStore, BaseRetriever]:
        try:
            auth = PasswordAuthenticator(couchbase_username, couchbase_password)
            options = ClusterOptions(auth)
            cluster = Cluster(couchbase_connection_string, options)

            cluster.wait_until_ready(timedelta(seconds=5))
        except Exception as e:
            raise ValueError(f"Failed to connect to Couchbase: {e}")
        documents = []
        for _input in inputs or []:
            if isinstance(_input, Record):
                documents.append(_input.to_lc_document())
            else:
                documents.append(_input)
        if documents:
            vector_store = CouchbaseVectorStore.from_documents(
                documents=documents,
                cluster=cluster,
                bucket_name=bucket_name,
                scope_name=scope_name,
                collection_name=collection_name,
                embedding=embedding,
                index_name=index_name,
            )
        else:
            vector_store = CouchbaseVectorStore(
                cluster=cluster,
                bucket_name=bucket_name,
                scope_name=scope_name,
                collection_name=collection_name,
                embedding=embedding,
                index_name=index_name,
            )
        return vector_store
