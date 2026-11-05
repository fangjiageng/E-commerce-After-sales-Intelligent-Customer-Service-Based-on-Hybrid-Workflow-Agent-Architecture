import json
import logging
from collections.abc import AsyncIterator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError

from app.graph import runtime
from app.schemas.chat import ChatRequest

logger = logging.getLogger(__name__)
router = APIRouter()

# SSE的格式是：每条消息以"data: "开头，后面跟着JSON字符串，最后以两个换行符结尾。客户端收到消息后，会触发onmessage事件，事件对象的data属性就是JSON字符串。
def _sse(payload: dict) -> str:
    return f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"  # ensure_ascii=False不能少，否则中文全变成转义序列，前端拿到一堆看不懂的东西

# SSE错误消息的格式是：每条消息以"event: error\n"开头，后面跟着"data: "和JSON字符串，最后以两个换行符结尾。客户端收到消息后，会触发onerror事件，事件对象的data属性就是JSON字符串。
def _sse_error(message: str) -> AsyncIterator[str]:
    yield "event: error\n"
    yield _sse({"message": message})


# 将输出挂载到路由，并返回一个StreamingResponse对象，表示一个流式响应。客户端可以通过EventSource对象来接收这个响应，并处理每条消息。
@router.post("/api/chat")
async def chat(req: ChatRequest):
    # 定义一个异步生成器函数event_stream，它会调用runtime.stream_turn方法来获取聊天的事件流。每当有新的事件产生时，它会根据事件的类型来生成相应的SSE消息
    # 并通过yield语句发送给客户端。
    async def event_stream() -> AsyncIterator[str]:
        try:
            async for ev in runtime.stream_turn(req.user_id, req.message, req.conversation_id):  
                if ev["type"] == "tool":
                    yield _sse({"event": "tool", "name": ev["name"]})
                elif ev["type"] == "delta":
                    yield _sse({"delta": ev["text"]})
                elif ev["type"] == "citations":
                    yield _sse({"event": "citations", "items": ev["items"]})
                elif ev["type"] == "interrupt":
                    # ch08:负载透传(select_order 带 orders / confirm_ticket 带 preview),前端按 kind 分发
                    yield _sse({"event": "interrupt",
                                **{k: v for k, v in ev.items() if k != "type"}})
                elif ev["type"] == "actions":
                    yield _sse({"event": "actions", "items": ev["items"]})
                elif ev["type"] == "done":
                    yield _sse({"event": "done", "conversation_id": ev["conversation_id"]})
        # 处理异常情况，包括会话不存在、数据库错误和其他异常。对于每种异常，都会记录日志，并通过SSE发送错误消息给客户端。
        except runtime.ConversationNotFound:
            for f in _sse_error("会话不存在"):
                yield f
            return
        except SQLAlchemyError:
            logger.exception("数据库错误 user_id=%s", req.user_id)
            for f in _sse_error("数据库暂时不可用,请稍后重试"):
                yield f
            return
        except Exception:
            logger.exception("图编排失败 user_id=%s", req.user_id)
            for f in _sse_error("上游模型暂时不可用,请稍后重试"):
                yield f
            return
        yield "data: [DONE]\n\n"

    # StreamingResponse是FastAPI提供的一个响应类，用于返回一个流式响应。
    # 它接受一个异步生成器函数作为参数，并指定媒体类型为"text/event-stream"，表示这是一个SSE响应。
    return StreamingResponse(event_stream(), media_type="text/event-stream")  
