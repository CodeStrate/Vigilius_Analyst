from pydantic import BaseModel, ConfigDict

class ChatModel(BaseModel):
    prompt: str

    model_config = ConfigDict(from_attributes=True,
        json_schema_extra={
            "example": {
                "prompt": "What is the average age of users?"
            }},
        extra="forbid")  # strict mode