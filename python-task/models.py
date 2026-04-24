from typing import List, Optional
from pydantic import BaseModel, Field

class Book(BaseModel):
    title: str
    author_name: List[str] = Field(default_factory=list)
    first_publish_year: Optional[int] = None
    key: str

class BookSearchResponse(BaseModel):
    numFound: int
    docs: List[Book] = Field(default_factory=list)
