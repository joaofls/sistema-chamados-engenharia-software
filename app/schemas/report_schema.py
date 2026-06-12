from pydantic import BaseModel


class ReportEntry(BaseModel):
    label: str
    total: int
