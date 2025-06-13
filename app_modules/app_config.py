import datetime

BASE_CHAT_DIR = "chats"

# --- Model Definitions ---
AVAILABLE_MODELS = {
    "Google Gemini 2.5 Pro": "gemini-2.5-pro-preview-05-06",
    "OpenAI GPT-4.1": "gpt-4.1",
}
DEFAULT_MODEL_NAME = "Google Gemini 2.5 Pro"

# --- FIXED MODEL CONFIGURATION ---
FIXED_MODEL_ID = "gemini-2.5-pro-preview-05-06"
MODEL_TO_USE_FOR_API = f"models/{FIXED_MODEL_ID}"

current_date_for_prompt = datetime.date.today().strftime('%B %d, %Y')

UNIFIED_SYSTEM_INSTRUCTION = (
    f"You are an expert financial assistant, specializing in the Indian stock market. "
    f"For your contextual understanding, the current real-world date is {current_date_for_prompt}. "
    "Your primary directive is to provide accurate and objective information.\n\n"
    "Guidelines for your response:\n"
    "1. For questions that can be answered from the provided document context, base your answer strictly and exclusively on that document. If the document does not contain sufficient information, clearly state so.\n"
    "2. For questions about current events, recent news, or general knowledge that is clearly outside the scope of the provided document, you should indicate that your primary function is to analyze the uploaded document but you can attempt to use tools for other specific data if available.\n"
    "3. When asked to fetch or compare specific historical stock prices or market index values for ANY GIVEN SPECIFIC DATE:\n"
    "   - Your internal knowledge about current or future dates may be outdated due to your training data's cutoff point. Therefore, you MUST NOT use this internal knowledge to pre-judge whether a given date is in the past or future relative to the real world. The provided current real-world date is for your reference.\n"
    "   - Your FIRST action for such requests is to use the appropriate financial tool. These tools are designed to retrieve historical data up to the most recently available trading day from their data sources.\n"
    "   - Use the 'get_historical_stock_price' tool if you need a stock's price. You will need to provide the stock symbol (e.g., 'RELIANCE.NS' for Reliance on NSE, 'INFY.BO' for Infosys on BSE, 'MSFT' for Microsoft on NASDAQ) and the specific date in 'YYYY-MM-DD' format.\n"
    "   - Use the 'get_historical_index_value' tool if you need the value of a market index (e.g., NIFTY 50, SENSEX). You will need to provide the index symbol (e.g., '^NSEI' for NIFTY 50, '^BSESN' for SENSEX) and the specific date in 'YYYY-MM-DD' format.\n"
    "   - Only after the tool provides a response (either data or an error message like 'no data found' or 'invalid date for tool'), should you formulate your answer. If the tool returns data, use it to answer the user's question or perform the comparison. If the tool indicates no data is available or an error occurred, report that specific information from the tool. Do not invent reasons if the tool fails; report the tool's feedback accurately.\n"
    "4. For retrieving specified Indian stock market index data (e.g., Nifty, Sensex) when not part of a comparison task, you can also use the 'get_historical_index_value' tool.\n"
    "5. Provide a concise, precise, and informative response that directly addresses the question.\n"
    "6. If the document context does not contain the specific information required to answer other types of questions accurately, you must clearly state: \"The provided context does not contain sufficient information to answer this question accurately.\" Do not attempt to guess or infer an answer for document-related questions.\n"
    "7. Maintain a professional and objective tone suitable for financial communication.\n"
    "8. Avoid any form of hallucination or speculation. Accuracy is paramount.\n"
    "9. If the user's question is ambiguous, state that the question is unclear and request the user to rephrase it for better clarity based on the document's content or the type of data they are seeking.\n"
    "10. Do not provide financial advice, investment recommendations, or opinions on future market movements, even if the document or fetched data contains data that could inform such an opinion. Stick to relaying factual information as presented in the document or fetched via tools.\n"
    "11. As an expert in the Indian stock market, interpret any domain-specific terminology found within the document accurately.\n"
    "12. When providing an answer using information from the document, you MUST cite the relevant page number at the end of the sentence. For example: 'The total tax paid was ₹15,000 (Page: 4)'. For multiple pages, use the format `(Pages: 4, 7)`."
    "13. If the user asks for a chart, graph, comparison, or any form of visual representation of data, you MUST use the `display_comparison_chart` tool. Extract the relevant labels and values from the document to pass as arguments to the tool."
    "14. When a user asks for a line graph of stock prices over a period, FIRST use the `get_historical_price_range` tool to fetch all the daily closing prices at once. THEN, pass the resulting data to the `display_comparison_chart` tool with `chart_type` set to 'line', `x_axis` set to 'Date', and `y_axis` set to 'Close'."
)

# --- Profile Configurations ---
PROFILE_CONFIGS = {
    "profile1": {
        "button_label": "Demo 1 Monarch",
        "page_title": "Personal Statement Q&A",
        "predefined_chats": {
            "01-Apr-2024 to 31-Mar-2025 1": "documents/demo1/doc1.pdf",
            "01-Apr-2024 to 31-Mar-2025 2": "documents/demo1/doc2.pdf",
            "01-Apr-2024 to 31-Mar-2025 3": "documents/demo1/doc3.pdf",
            "01-Apr-2024 to 31-Mar-2025 4": "documents/demo1/doc4.pdf",
            "01-Apr-2024 to 31-Mar-2025 5": "documents/demo1/doc5.pdf",
            "01-Apr-2024 to 31-Mar-2025 6": "documents/demo1/doc6.pdf",
        },
        "questions": [
            "What is the date range of the given statement?",
            "Did i make an overall profit or loss? What was my grand total?",
            "What was my most profitable segment?",
            "Overall, how much did i spend on tax?",
            "In each segment, which stock gave me the highest realized gain?",
            "Which of my stocks has had the longest holding period?",
            "Which stock have i bought the highest quantity of?",
            "Which stock have i sold the highest quantity of?",
            "Which of my assets has the highest notional gain?",
            "Did i incur a loss in any segment?",
            "What was my greatest expense?",
            "Did any segment have a higher expense than gain?",
            "Were there any significant loss-making short-term cash trades? Which ones?",
            "What was the largest single loss from an F&O transaction?",
            "Which stock holding shows the largest notional loss as of the statement date?",
            "What is the total buy value of the assets currently held?",
            "Are there any open positions in F&O or Commodities, and what is their notional P&L?",
            "What was the single biggest profit made from one short-term stock trade listed?",
            "what is my single most profitable trade",
        ],
    },
    "profile2": {
        "button_label": "Demo 2 Kunvarji",
        "page_title": "Personal Statement Q&A",
        "predefined_chats": {
            "01-Apr-2024 to 31-Mar-2025 1": "documents/demo2/doc1.pdf",
            "01-Apr-2024 to 31-Mar-2025 2": "documents/demo2/doc2.pdf",
            "01-Apr-2024 to 31-Mar-2025 3": "documents/demo2/doc3.pdf",
            "01-Apr-2024 to 31-Mar-2025 4": "documents/demo2/doc4.pdf",
            "01-Apr-2024 to 31-Mar-2025 5": "documents/demo2/doc5.pdf",
            "01-Apr-2024 to 31-Mar-2025 6": "documents/demo2/doc6.pdf",
        },
        "questions": [
            "What is the date range of the given statement?",
            "Did i make an overall profit or loss? What was my grand total?",
            "What was my most profitable segment?",
            "Overall, how much did i spend on tax?",
            "In each segment, which stock gave me the highest realized gain?",
            "Which of my stocks has had the longest holding period?",
            "Which stock have i bought the highest quantity of?",
            "Which stock have i sold the highest quantity of?",
            "Which of my assets has the highest notional gain?",
            "Did i incur a loss in any segment?",
            "What was my greatest expense?",
            "Did any segment have a higher expense than gain?",
            "Were there any significant loss-making short-term cash trades? Which ones?",
            "What was the largest single loss from an F&O transaction?",
            "Which stock holding shows the largest notional loss as of the statement date?",
            "What is the total buy value of the assets currently held?",
            "Are there any open positions in F&O or Commodities, and what is their notional P&L?",
            "What was the single biggest profit made from one short-term stock trade listed?",
            "what is my single most profitable trade",
        ],
    },
    "profile3": {
        "button_label": "Demo 3 Nirmal Bang",
        "page_title": "ITR Statement Q&A",
        "predefined_chats": {
            "FY 2024-2025 1": "documents/demo3/doc1.pdf",
            "FY 2024-2025 2": "documents/demo3/doc2.pdf",
            "FY 2024-2025 3": "documents/demo3/doc3.pdf",
            "FY 2024-2025 4": "documents/demo3/doc4.pdf",
            "FY 2024-2025 5": "documents/demo3/doc5.pdf",
            "FY 2024-2025 6": "documents/demo3/doc6.pdf",
        },
        "questions": [
            "What investments do I currently hold? ",
            "Can you list the names of all the companies I have invested in? ",
            "What is the total value of my investments? ",
            "What is the value of my 'Free Balance' holdings? ",
            "What is the value of my 'Pledge' holdings? ",
            "Are there different categories of holdings, like 'Free Balance' or 'Pledge'? If so, what do they mean? ",
            "What was my opening balance at the beginning of the financial year? ",
            "What do 'Dr. Amount' and 'Cr. Amount' refer to in the ledger? ",
            "What are my total short-term capital gains/losses? ",
            "What are my total long-term capital gains/losses? ",
            "What is my total speculative profit or loss? ",
            "What does 'Os Purchase Qty' or 'Os Purchase Value' mean? ",
            "What should I do if I find any discrepancies in the statement? ",
            "Are there any important notes or disclaimers I should be aware of? ",
        ],
    },
    "profile4": {
        "button_label": "Demo 4 CDSL",
        "page_title": "CAS Statement Q&A",
        "predefined_chats": {
            "CAS April 2025 1": "documents/demo4/doc1.pdf",
            "CAS April 2025 2": "documents/demo4/doc2.pdf",
            "CAS April 2025 3": "documents/demo4/doc3.pdf",
            "CAS April 2025 4": "documents/demo4/doc4.pdf",
            "CAS April 2025 5": "documents/demo4/doc5.pdf",
            "CAS April 2025 6": "documents/demo4/doc6.pdf",
        },
        "questions": [
            "What is the total value of my investments as of the statement date? ",
            "How has the value of my portfolio changed over the past year? ",
            "What is the percentage breakdown of my investments across different asset classes like equity and debt? ",
            "Can you show me a summary of my investments held individually and jointly? ",
            "What are the equity shares I currently hold in my demat account? ",
            "What is the total value of my stock holdings? ",
            "Can you list the bonds I have in my portfolio and their current market value? ",
            "Have there been any transactions in my demat account during the period of this statement? ",
            "Which mutual fund schemes am I invested in? ",
            "What is the total value of all my mutual fund investments? ",
            "For each given mutual fund, what is the initial investment amount and what is its current value? ",
            "Can you show me the recent transactions in my mutual fund folios? ",
            "What are the exit load charges for my mutual fund schemes? ",
            "What is the current value of my NPS account? ",
        ],
    },
}