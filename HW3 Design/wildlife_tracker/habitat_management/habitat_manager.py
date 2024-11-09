from typing import Optional, List

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.animal_managment.animal import Animal
#handles the creation of habitats, their details (such as size, environment, and location), and the assignment of animals to them

class HabitatManager:
    def __init__(self) -> None: 
        habitats: dict[int, Habitat] = {}
        animals: List[int] = []
    
    def create_habitat(habitat_id: int, geographic_area: str, size: int, environment_type: str) -> Habitat:
        pass

    def get_habitat_by_id(self, habitat_id: int) -> Habitat:
        pass

    def remove_habitat(habitat_id: int) -> None:
        pass

    def get_habitats_by_geographic_area(self, geographic_area: str) -> List[Habitat]:
        pass

    def get_habitats_by_size(self, size: int) -> List[Habitat]:
        pass

    def get_habitats_by_type(self, environment_type: str) -> List[Habitat]:
        pass
    

