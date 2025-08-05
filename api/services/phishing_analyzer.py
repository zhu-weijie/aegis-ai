from langchain.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

PROMPT_TEMPLATE = """
Act as a cybersecurity analyst. Analyze the following email content
for signs of phishing.
Provide a short, one-sentence justification for your decision
and a risk score from 1 (low risk) to 10 (high risk).
Return your answer ONLY in the following format, with no other text:
Justification: [Your one-sentence justification here]
Risk Score: [Your score here]

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
        justification = (
            output_text.split("Justification:")[1].split("Risk Score:")[0].strip()
        )
        risk_score = int(output_text.split("Risk Score:")[1].strip())
        return {"justification": justification, "risk_score": risk_score}
    except (IndexError, ValueError) as e:
        print(f"Error parsing LLM output: {e}")
        return {
            "justification": "Failed to parse analysis from LLM.",
            "risk_score": -1,
        }
