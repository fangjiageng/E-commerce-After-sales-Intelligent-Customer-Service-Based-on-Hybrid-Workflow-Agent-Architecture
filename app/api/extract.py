# 本文件是主要负责从用户的售后描述中提取结构化工单信息。它使用了FastAPI框架来定义API路由，并依赖LangChain库来处理自然语言处理任务。
import logging

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.runnables import Runnable

from app.core.llm import get_chat_model
from app.core.prompts import EXTRACT_PROMPT
from app.schemas.extract import AfterSalesTicket, ExtractRequest

logger = logging.getLogger(__name__)
router = APIRouter()


# get_extractor函数是一个依赖注入函数，它返回一个可调用的提取器。
# 提取器是由EXTRACT_PROMPT和一个结构化输出模型AfterSalesTicket组成的流水线。
# 这个流水线会将用户输入的文本传递给模型，并将模型的输出约束为AfterSalesTicket结构化数据。
def get_extractor() -> Runnable:
    model = get_chat_model()
    return EXTRACT_PROMPT | model.with_structured_output(AfterSalesTicket)  # 对模型输出约束为 AfterSalesTicket 结构化数据 


# 把提取器逻辑挂载到FastAPI路由
@router.post("/api/extract", response_model=AfterSalesTicket)
async def extract(
    # 依赖注入让这条链每次请求现建，代价是多了一点对象构建开销，好处是测试时能整条替换掉，不用打补丁
    req: ExtractRequest, extractor: Runnable = Depends(get_extractor)  
) -> AfterSalesTicket:
    try:
        return await extractor.ainvoke({"text": req.text})
    except Exception as exc:
        logger.exception("结构化提取失败")
        raise HTTPException(status_code=502, detail="上游模型暂时不可用,请稍后重试") from exc
