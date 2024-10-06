from typing import Any

class Migration:

    def __init__(self,
                migration_id: int,
                status: str = "Scheduled") -> None:
        
        self.migration_id = migration_id
        self.status = status
        self.species = species

    def get_migration_details(self) -> dict[str, Any]:
       pass

    def update_migration_details(self, **kwargs: Any) -> None:
        pass

    