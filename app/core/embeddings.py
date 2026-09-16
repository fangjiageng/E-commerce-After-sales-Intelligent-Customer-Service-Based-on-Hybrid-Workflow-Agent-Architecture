from openai import AsyncOpenAI

from app.config import settings

_CLIENT: AsyncOpenAI | None = None


def _client() -> AsyncOpenAI:
    """直连嵌入上游(硅基流动的 bge-m3,OpenAI 兼容)。
    进程内单例（整个进程里只建一个连接对象）:复用同一 httpx 连接池,避免每次 embed 新建客户端累积连接/fd。"""
    # _client() 用全局变量 + 判空实现：无论 embed_texts / embed_query 被调多少次，AsyncOpenAI 客户端只 new 一次，后续全部复用。
    # AsyncOpenAI 底层包着一个 httpx 客户端，每新建一个实例就会新开 TCP 连接、占用文件描述符（fd）。
    # 如果每次 embed 都 AsyncOpenAI(...) 新建，建库那种成百上千次的调用，连接和 fd 会一路累积，很快把进程的连接数 / 文件描述符撑爆。
    # 单例只建一次，httpx 连接池被反复复用，这是它存在的核心原因。
    global _CLIENT
    if _CLIENT is None:
        _CLIENT = AsyncOpenAI(base_url=settings.embed_base_url, api_key=settings.embed_api_key)
    return _CLIENT


async def embed_texts(texts: list[str]) -> list[list[float]]:
    resp = await _client().embeddings.create(model=settings.embed_model, input=texts)
    return [d.embedding for d in resp.data]


async def embed_query(text: str) -> list[float]:
    return (await embed_texts([text]))[0]
