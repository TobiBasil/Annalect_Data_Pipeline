from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRecord(BaseModel):
    """
    Strict schema for a single cleaned user record.
    """

    name: str
    gender: Literal["male", "female", "other"]
    city: str
    state: str
    country: str
    email: EmailStr
    age: int = Field(ge=0, le=120, examples=[30])
    registration_date: datetime

    # Validation logic to ensure the date is not in the future.
    @field_validator("registration_date")
    @classmethod
    def date_not_in_future(cls, v: datetime) -> datetime:
        if v > datetime.now(v.tzinfo):
            raise ValueError("Registration date cannot be in the future")
        return v

    model_config = {"str_strip_whitespace": True,}
