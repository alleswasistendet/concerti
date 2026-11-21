from dataclasses import dataclass


@dataclass
class Concert:
    date: str
    title: str
    institution: str | None = None
    price: float = 0.0
    typology: str | None = None
    subtypology: str | None = None
    program: str | None = None
    comment: str | None = None
