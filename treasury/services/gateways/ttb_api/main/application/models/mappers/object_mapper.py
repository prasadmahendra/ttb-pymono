from __future__ import annotations

from typing import TypeVar, Type, Any, TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from strawberry.experimental.pydantic.object_type import StrawberryTypeFromPydantic

class ObjectMapper:

    SourceModelType = TypeVar("SourceModelType", bound=BaseModel) # noqa
    TargetModelType = TypeVar("TargetModelType", bound=(BaseModel)) # noqa

    @classmethod
    def map(cls, source: SourceModelType, target_class: Type[TargetModelType | StrawberryTypeFromPydantic[Any]]) -> TargetModelType:
        if source is None:
            return target_class.model_validate({})
        if not isinstance(source, BaseModel):
            raise ValueError(f"Invalid source model: Expected an instance of BaseModel, got {type(source).__name__}")

        if hasattr(target_class, "to_pydantic") and hasattr(target_class, "from_pydantic"):
            # Handle Strawberry Pydantic types
            return target_class.from_pydantic(source) # type: ignore

        return target_class.model_validate(
            source.model_dump(mode="json")
        )

    @classmethod
    def map_list(cls, source_list: list[SourceModelType], target_class: Type[TargetModelType | StrawberryTypeFromPydantic[Any]]) -> list[TargetModelType]:
        return [cls.map(source=source_item, target_class=target_class) for source_item in source_list]