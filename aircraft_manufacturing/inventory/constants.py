from dataclasses import dataclass

@dataclass(frozen=True)
class DefaultPartTypes:
    WING: str = 'WING'
    BODY: str = 'BODY'
    TAIL: str = 'TAIL'
    AVIONICS: str = 'AVIONICS'