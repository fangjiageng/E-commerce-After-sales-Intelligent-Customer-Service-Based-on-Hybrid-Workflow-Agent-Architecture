from dataclasses import dataclass

from app.kb import chunking

_KEY_TERMS = ("退款", "退货", "时效", "运费", "邮费", "费用", "保修", "赔偿", "期限", "包邮")
# ch09 起跨模块复用(confidence 关键条款信号 / review 写回打标),导出公共名
KEY_TERMS = _KEY_TERMS


@dataclass
class Chunk:
    category: str
    questions: str
    answer: str
    section_path: str
    content_type: str
    is_key_clause: int = 0


def _is_key(title: str, body: str) -> int:
    # 关键条款单独打标，判断时只看标题加正文前四十个字，因为关键词出现在开头才说明这一块讲的就是这件事，避免只提一嘴就被标记为关键条款
    head = title + body[:40]
    return int(any(t in head for t in _KEY_TERMS))


is_key = _is_key   # ch09 起跨模块复用(审核写回打关键条款标),导出公共名


def build_chunks(
    md: str, content_type: str,
    chunk_size: int = 400, overlap: int = 60, table_max_rows: int = 10,
) -> list[Chunk]:
    # 原文档切完后在这里串成一条线
    out: list[Chunk] = []
    for sec in chunking.split_sections(md):
        path = [sec.metadata[k] for k in ("h1", "h2", "h3", "h4") if sec.metadata.get(k)]
        section_path = " / ".join(path)
        title = path[-1] if path else content_type
        # category:政策/手册用上级标题路径;顶层无上级则用 content_type
        category = " / ".join(path[:-1]) if len(path) > 1 else (path[0] if path else content_type)
        body = sec.page_content.strip()
        if not body:
            continue
        if chunking.is_table_block(body):
            pieces = chunking.split_table_rows(body, table_max_rows)
        else:
            base = chunking.recursive_split(body, chunk_size, chunk_overlap=0)
            pieces = chunking.apply_sentence_overlap(base, overlap)
        for piece in pieces:
            # 切分时被strip_headers摘走的标题派上用场：整条标题路径拼成section_path用来溯源，最后一级标题当做questions，上级路径当作category
            out.append(Chunk(
                category=category, questions=title, answer=piece,
                section_path=section_path, 
                content_type=content_type,
                is_key_clause=_is_key(title, piece),
            ))
    return out
