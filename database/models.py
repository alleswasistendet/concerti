from dataclasses import dataclass


@dataclass
class Concert:
    date: str
    title: str
    institution: str | None = None
    price: float | None = None
    typology: str | None = None
    subtypology: str | None = None
    program: str | None = None
    comment: str | None = None
