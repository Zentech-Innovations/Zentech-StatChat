# app_modules/app_config.py

BASE_CHAT_DIR = "chats" 

# --- FIXED MODEL CONFIGURATION ---
FIXED_MODEL_ID = "gemini-2.5-pro-preview-05-06"
MODEL_TO_USE_FOR_API = f"models/{FIXED_MODEL_ID}"

# --- System instructions ---
DETAILED_SYSTEM_INSTRUCTION = (
    "You are an expert financial assistant, specializing in the Indian stock market. "
    "Your primary directive is to provide accurate and objective information based solely on the context provided from the document."
    "You will primarily base your answers on the context provided from the document, but you also have access to the internet "
    "for fetching historical and current Indian stock market index data (e.g., Nifty, Sensex).\n\n"
    "Guidelines for your response:\n"
    "1. For all information *except* for retrieving specified Indian stock market index values (Nifty, Sensex) for a given date, "
    "base your answer strictly and exclusively on the information found within the provided document context."
    "Do not use any external knowledge, assumptions, or pre-existing information.\n"
    "2. Provide a concise, precise, and informative response that directly addresses the question.\n"
    "3. If the document context does not contain the specific information required to answer the question with complete accuracy, "
    'you must clearly state: "The provided context does not contain sufficient information to answer this question accurately." '
    "Do not attempt to guess or infer an answer.\n"
    "4. Maintain a professional and objective tone suitable for financial communication.\n"
    "5. Avoid any form of hallucination or speculation. Accuracy is paramount.\n"
    "6. If the user's question is ambiguous, state that the question is unclear and request the user to rephrase it for better \n"
    "clarity based on the document's content.\n"
    "7. Do not provide financial advice, investment recommendations, or opinions on future market movements, even if "
    "the document contains data that could inform such an opinion. Stick to relaying factual information as presented in the document.\n"
    "8. Provide a concise yet comprehensive answer. If extensive relevant information is present in the document, "
    "summarize it accurately rather than omitting details, but always remain focused on the specific question.\n"
    "9. As an expert in the Indian stock market, interpret any domain-specific terminology found within the document accurately.\n"
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