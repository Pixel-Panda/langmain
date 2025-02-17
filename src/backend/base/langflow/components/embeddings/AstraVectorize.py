from typing import Any
from langflow.custom import Component
from langflow.inputs.inputs import DictInput, SecretStrInput, MessageTextInput, DropdownInput
from langflow.template.field.base import Output


class AstraVectorize(Component):
    display_name: str = "Astra Vectorize"
    description: str = "Configuration options for Astra Vectorize server-side embeddings."
    documentation: str = "https://docs.datastax.com/en/astra-db-serverless/databases/embedding-generation.html"
    icon = "AstraDB"
    name = "AstraVectorize"

    VECTORIZE_PROVIDERS_MAPPING = {
        "Azure OpenAI": ["azureOpenAI", ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]],
        "Hugging Face - Dedicated": ["huggingfaceDedicated", ["endpoint-defined-model"]],
        "Hugging Face - Serverless": [
            "huggingface",
            [
                "sentence-transformers/all-MiniLM-L6-v2",
                "intfloat/multilingual-e5-large",
                "intfloat/multilingual-e5-large-instruct",
                "BAAI/bge-small-en-v1.5",
                "BAAI/bge-base-en-v1.5",
                "BAAI/bge-large-en-v1.5",
            ],
        ],
        "Jina AI": [
            "jinaAI",
            [
                "jina-embeddings-v2-base-en",
                "jina-embeddings-v2-base-de",
                "jina-embeddings-v2-base-es",
                "jina-embeddings-v2-base-code",
                "jina-embeddings-v2-base-zh",
            ],
        ],
        "Mistral AI": ["mistral", ["mistral-embed"]],
        "NVIDIA": ["nvidia", ["NV-Embed-QA"]],
        "OpenAI": ["openai", ["text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002"]],
        "Upstage": ["upstageAI", ["solar-embedding-1-large"]],
        "Voyage AI": [
            "voyageAI",
            ["voyage-large-2-instruct", "voyage-law-2", "voyage-code-2", "voyage-large-2", "voyage-2"],
        ],
    }
    VECTORIZE_MODELS_STR = "\n\n".join(
        [provider + ": " + (", ".join(models[1])) for provider, models in VECTORIZE_PROVIDERS_MAPPING.items()]
    )

    inputs = [
        DropdownInput(
            name="provider",
            display_name="Provider",
            options=VECTORIZE_PROVIDERS_MAPPING.keys(),
            value="",
            required=True,
        ),
        MessageTextInput(
            name="model_name",
            display_name="Model Name",
            info=f"The embedding model to use for the selected provider. Each provider has a different set of models "
            f"available (https://docs.datastax.com/en/astra-db-serverless/databases/embedding-generation.html):\n\n{VECTORIZE_MODELS_STR}",
            required=True,
        ),
        SecretStrInput(
            name="provider_api_key",
            display_name="Provider API Key",
            info="An alternative to the Astra Authentication that passes an API key for the provider with each request to Astra DB. This may be used when Vectorize is configured for the collection, but no corresponding provider secret is stored within Astra's key management system.",
        ),
        MessageTextInput(
            name="api_key_name",
            display_name="Provider API Key Name",
            info="The name of the embeddings provider API key stored on Astra. If set, it will override the 'ProviderKey' in the authentication parameters.",
            advanced=True,
        ),
        DictInput(
            name="authentication",
            display_name="Authentication Parameters",
            is_list=True,
            advanced=True,
        ),
        DictInput(
            name="model_parameters",
            display_name="Model Parameters",
            advanced=True,
            is_list=True,
        ),
    ]
    outputs = [
        Output(display_name="Vectorize", name="config", method="build_options", types=["dict"]),
    ]

    def build_options(self) -> dict[str, Any]:
        provider_value = self.VECTORIZE_PROVIDERS_MAPPING[self.provider][0]
        authentication = {**self.authentication}
        api_key_name = self.api_key_name
        if api_key_name:
            authentication["providerKey"] = api_key_name
        return {
            # must match astrapy.info.CollectionVectorServiceOptions
            "collection_vector_service_options": {
                "provider": provider_value,
                "modelName": self.model_name,
                "authentication": authentication,
                "parameters": self.model_parameters,
            },
            "collection_embedding_api_key": self.provider_api_key,
        }
