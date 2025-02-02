"""Constants for assembly app."""
from dataclasses import dataclass
from typing import List, Tuple, Dict
from inventory.constants import DefaultPartTypes

# Aircraft types, not dynamic as expected
@dataclass(frozen=True)
class DefaultAircraftTypes:
    AKINCI: str = 'AKINCI'
    KIZILELMA: str = 'KIZILELMA'
    TB2: str = 'TB2'
    TB3: str = 'TB3'

# Required parts for each aircraft type, not dynamic as expected
DEFAULT_AIRCRAFT_REQUIRED_PARTS: Dict[str, Dict[str, int]] = {
    DefaultAircraftTypes.TB2: {
        DefaultPartTypes.WING: 2,
        DefaultPartTypes.BODY: 1,
        DefaultPartTypes.TAIL: 1,
        DefaultPartTypes.AVIONICS: 1
    },
    DefaultAircraftTypes.TB3: {
        DefaultPartTypes.WING: 2,
        DefaultPartTypes.BODY: 1,
        DefaultPartTypes.TAIL: 1,
        DefaultPartTypes.AVIONICS: 2
    },
    DefaultAircraftTypes.AKINCI: {
        DefaultPartTypes.WING: 2,
        DefaultPartTypes.BODY: 1,
        DefaultPartTypes.TAIL: 2,
        DefaultPartTypes.AVIONICS: 2
    },
    DefaultAircraftTypes.KIZILELMA: {
        DefaultPartTypes.WING: 4,
        DefaultPartTypes.BODY: 1,
        DefaultPartTypes.TAIL: 1,
        DefaultPartTypes.AVIONICS: 2
    }
} 