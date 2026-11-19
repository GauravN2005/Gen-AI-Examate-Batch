
from dataclasses import asdict, dataclass


@dataclass
class Record:
    concept: str
    plain_definition: str
    example: str
    module_chapter: str
    risk_warning: str
    source_url: str

    def to_dict(self):
        return asdict(self)
