from app.domain.interfaces import DatasetRepository
from app.domain.models import DatasetMetadata, DatasetSnapshot


class DatasetService:
    def __init__(self, repository: DatasetRepository):
        self.repository = repository

    def list_datasets(self) -> list[DatasetMetadata]:
        return self.repository.list_datasets()

    def get_dataset(self, dataset_id: str) -> DatasetSnapshot:
        return self.repository.get_dataset(dataset_id)

    def upload_csv(self, filename: str, content: bytes) -> DatasetMetadata:
        return self.repository.save_csv(filename, content)
