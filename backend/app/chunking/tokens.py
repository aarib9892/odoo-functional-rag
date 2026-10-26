from importlib.metadata import version

import tiktoken

ENCODING_NAME = "cl100k_base"
TOKENIZER_VERSION = version("tiktoken")
_encoding = tiktoken.get_encoding(ENCODING_NAME)


def count_tokens(text: str) -> int:
    return len(_encoding.encode_ordinary(text))
