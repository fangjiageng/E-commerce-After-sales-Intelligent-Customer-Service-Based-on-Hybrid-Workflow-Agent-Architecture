# 本文件实现问法归一化去重
import re

# 下面这行代码实现结果：“运费怎么算？”和“运费怎么算”属于同一个键
_STRIP_RE = re.compile(r"[\s\W_]+", re.UNICODE)  # \W 不含中文(中文属 \w),故只去空白/标点，不会去掉中文


def normalize_question(q: str) -> str:
    return _STRIP_RE.sub("", q.strip().lower())


def dedupe(items: list, existing_questions: list[str]) -> tuple[list, list]:
    """去重:staging 内部 + 对已有 knowledge 问法;返回 (kept, discarded)。"""
    # seen一开始就装进了库里已有的全部问法，一次遍历挡住了本批内部重复和存量重复
    seen = {normalize_question(q) for q in existing_questions}
    kept, discarded = [], []
    for item in items:
        key = normalize_question(item.question)
        if not key or key in seen:
            discarded.append(item)
        else:
            seen.add(key)
            kept.append(item)
    return kept, discarded
