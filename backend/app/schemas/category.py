from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    category_id: str = Field(min_length=1, max_length=100)
    display_name: str = Field(min_length=1, max_length=200)
    destination_template: str = Field(min_length=1)
    enabled: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(CategoryBase):
    pass


class CategoryRead(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
