from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_tracking.migration import Migration 

#specifying starting and ending habitats, species involved, and migration duration

class MigrationPath:

    def __init__(self,
                path_id: int,
                start_date: str,
                start_location: Habitat,
                destination: Habitat,
                duration: Optional[int] = None,
                migrations: dict[int, Migration] = {},
                species: str,
                status: str = "Scheduled") -> None:
        
        self.path_id = path_id
        self.start_date = start_date
        self.start_location = start_location
        self.destination = destination
        self.duration = duration
        self.status = status

    def get_migration_path_details(self) -> dict:
        pass

    def update_migration_path_details(self, **kwargs) -> None:
        pass
