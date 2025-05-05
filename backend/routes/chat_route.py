from handlers.chat_handler import OpenAIChatHandler
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from backend.models.chatModel import ChatModel

router = APIRouter()
handler = OpenAIChatHandler()

@router.get("/chat_help", status_code=status.HTTP_200_OK)
async def chat_help():
    """
    Endpoint to provide help information about the chat functionality.
    """
    return JSONResponse(status_code=status.HTTP_200_OK,
                        content={"message": '''
    Hello I am QueryLlama, your AI assistant. I can help you with data analysis.
    You can ask me questions about data analysis and SQL coding, and I will provide you information and code snippets to help you out.'''})

@router.post("/chat", status_code=status.HTTP_200_OK)
async def start_chat(payload: ChatModel):
    client = handler.client
    try:
        response = client.chat.completions.create(
            model=handler.model_preference,
            messages=[
                {"role": "system", "content": '''You are a helpful assistant that helps users with data analysis and teach SQL coding. You provide information and code snippets to help them out.
                 In case user asks something that is not related to data analysis or SQL coding, you will politely decline to answer.'''},
                {"role": "user", "content": payload.prompt}
            ],
            temperature=0.3,
            stream=False
        )
        ai_reply = response.choices[0].message.content
        return JSONResponse(status_code=status.HTTP_200_OK, content={"ai_response": ai_reply.strip()})

    except HTTPException as http_ex:
        print(f"HTTP Exception: {http_ex}")
        raise HTTPException(status_code=http_ex.status_code, detail=http_ex.detail)

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="There was an issue starting the conversation. Please try again.")
