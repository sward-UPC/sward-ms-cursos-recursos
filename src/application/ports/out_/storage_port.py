from abc import ABC, abstractmethod


class StoragePort(ABC):
    @abstractmethod
    async def get_url(self, s3_key: str) -> str: ...
    @abstractmethod
    async def upload(self, s3_key: str, content: bytes, content_type: str) -> str: ...
