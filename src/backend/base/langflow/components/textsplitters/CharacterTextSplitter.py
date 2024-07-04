from typing import List, Any

from langchain_text_splitters import CharacterTextSplitter, TextSplitter

from langflow.base.textsplitters.model import LCTextSplitterComponent
from langflow.inputs import IntInput, DataInput, MessageTextInput
from langflow.schema import Data
from langflow.utils.util import unescape_string


class CharacterTextSplitterComponent(LCTextSplitterComponent):
    display_name = "CharacterTextSplitter"
    description = "Split text by number of characters."
    documentation = "https://docs.langflow.org/components/text-splitters#charactertextsplitter"
    name = "CharacterTextSplitter"

    inputs = [
        IntInput(
            name="chunk_size",
            display_name="Chunk Size",
            info="The maximum length of each chunk.",
            value=1000,
        ),
        IntInput(
            name="chunk_overlap",
            display_name="Chunk Overlap",
            info="The amount of overlap between chunks.",
            value=200,
        ),
        DataInput(
            name="data_input",
            display_name="Input",
            info="The texts to split.",
            input_types=["Document", "Data"],
        ),
        MessageTextInput(
            name="separator",
            display_name="Separator",
            info='The characters to split on.\nIf left empty defaults to "\\n\\n".',
        ),
    ]

    def get_data_input(self) -> Any:
        return self.data_input

    def build_text_splitter(self) -> TextSplitter:
        if self.separator:
            separator = unescape_string(self.separator)
        else:
            separator = "\n\n"
        return CharacterTextSplitter(
            chunk_overlap=self.chunk_overlap,
            chunk_size=self.chunk_size,
            separator=separator,
        )
