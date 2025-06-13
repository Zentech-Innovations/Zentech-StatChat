from . import finance_tool, visualization_tool


ALL_GEMINI_TOOLS = [
    finance_tool.GEMINI_GET_STOCK_PRICE,
    finance_tool.GEMINI_GET_INDEX_VALUE,
    finance_tool.GEMINI_GET_PRICE_RANGE,
    visualization_tool.VISUALIZATION_TOOL_GEMINI
]
ALL_OPENAI_TOOLS = [
    finance_tool.OPENAI_GET_STOCK_PRICE,
    finance_tool.OPENAI_GET_INDEX_VALUE,
    finance_tool.OPENAI_GET_PRICE_RANGE,
    visualization_tool.VISUALIZATION_TOOL_OPENAI,
]

TOOL_IMPLEMENTATIONS = {
    "get_historical_stock_price": finance_tool.get_historical_stock_price_impl,
    "get_historical_index_value": finance_tool.get_historical_index_value_impl,
    "get_historical_price_range": finance_tool.get_historical_price_range_impl,
    "display_comparison_chart": visualization_tool.create_comparison_chart
}
