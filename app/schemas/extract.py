from enum import Enum

from pydantic import BaseModel, Field, field_validator


class ExtractRequest(BaseModel):
    text: str = Field(min_length=1, description="用户的售后描述原文")


class RequestType(str, Enum):
    REFUND = "退款"
    EXCHANGE = "换货"
    REPAIR = "维修"
    COMPLAINT = "投诉"
    OTHER = "其他"


class AfterSalesTicket(BaseModel):
    """从用户售后描述中提取的结构化工单。"""
    # Field()函数用于定义模型字段的元数据和验证规则。description参数会被翻译成模型看到的schema，跟System Prompt一样属于提示词的一部分
    order_id: str | None = Field(
        default=None, description="订单号,原文未出现则为 null,禁止编造"
    )
    request_type: RequestType = Field(description="用户诉求类型")
    expected_solution: str = Field(description="用户期望的处理方案,一句话概括")

    # 函数逻辑：大模型很容易犯的毛病：明明没有订单号，不输出null，反而输出字符串"null"/"无"/"none"。
    # 这个校验器就是为了解决该问题。在订单进来时，先把这些字符串统一转换成Python的None。这样在后续处理时，就不会误认为有订单号存在。
    @field_validator("order_id", mode="before")
    @classmethod
    def _normalize_missing_order_id(cls, v: object) -> object:
        # 模型偶尔把"没有订单号"表达成占位字符串而非省略参数,统一归一为 None
        if isinstance(v, str) and v.strip().lower() in {"", "null", "none", "n/a", "无"}:
            return None
        return v
