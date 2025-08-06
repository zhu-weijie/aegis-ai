import json

from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

PROMPT_TEMPLATE = """
Act as a cybersecurity analyst. Analyze the following email content
for signs of phishing.

1.  Provide a short, one-sentence justification for your decision.
2.  Provide a risk score from 1 (low risk) to 10 (high risk).
3.  Extract Indicators of Compromise (IoCs). Extract all URLs, domains,
and email addresses.

Return your answer ONLY as a valid JSON object with the following keys:
"justification", "risk_score", "iocs".
The "iocs" value should be an object with keys "urls", "domains", and "emails".

Example Response:
{{
  "justification": "The email creates a false sense of urgency and "
  "contains a suspicious link.",
  "risk_score": 8,
  "iocs": {{
    "urls": ["http://suspicious-link.com/login"],
    "domains": ["suspicious-link.com"],
    "emails": ["sender@example.com"]
  }}
}}

Email Content:
---
Sender: {sender}
Subject: {subject}
Body: {body}
---
"""


def analyze_email_content(sender: str, subject: str, body: str) -> dict:
    prompt = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    chain = prompt | llm | StrOutputParser()

    output_text = chain.invoke({"sender": sender, "subject": subject, "body": body})

    try:
        result = json.loads(output_text)
        result.setdefault("iocs", {})
        result["iocs"].setdefault("urls", [])
        result["iocs"].setdefault("domains", [])
        result["iocs"].setdefault("emails", [sender])
        return result
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing LLM JSON output: {e}")
        return {
            "justification": "Failed to parse analysis from LLM.",
            "risk_score": -1,
            "iocs": {"urls": [], "domains": [], "emails": [sender]},
        }
