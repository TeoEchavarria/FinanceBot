import json
import os
from openai import OpenAI

class FinanceManager:
    @staticmethod
    def get(query: str, list_debts, membership: str) -> dict:
        """
        membership: 'free' => use local Ollama; 'pro' => normal OpenAI usage
        """

        if membership == "free":
            # Connect to Ollama locally
            client = OpenAI(
                base_url="http://localhost:11434/v1",  # default Ollama port
                api_key="ollama-local"                 # can be any string
            )
        elif membership == "pro":
            # Use your OpenAI API key from environment or wherever you store it
            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        else:
            raise ValueError("Invalid membership type. Use 'free' or 'pro'.")

        prompt = "You are a financial assistant specialized in analyzing financial transactions. Your task is to identify and classify payments in any financial situation provided by the user. Extract the following information: 1) Debt: Identify the type of debt based on a predefined list of categories (referred to as debt_list); 2) Description: Provide a brief description of the payment; 3) Amount: Extract the payment amount as a number without a sign; 4) Type: Classify the transaction as Positive if money is incoming or Negative if money is outgoing. Respond with this information in a clear and structured format." if membership == "pro" else "You are a highly specialized Financial Transaction Classification Model. Your primary objective is to analyze and classify each transaction in the user’s input with utmost accuracy.  Objectives: 1. Identify “Pockets”: Detect the category or “pocket” where the money or debt is allocated (e.g., savings, rent, groceries, loans). 2. Extract Description: Provide a concise explanation or context for each transaction (e.g., rent payment, salary deposit, grocery shopping). 3. Extract Amount: Capture the amount mentioned in each transaction as a plain number (no plus + or minus - sign). 4. Classify Transaction Type: - Positive if the user mentions receiving money (e.g., “I got paid,” “I received,” “they gave me”). - Negative if the user mentions spending money (e.g., “I paid,” “I bought,” “I spent”).  Detailed Instructions: 1. Segment the User Input: Break down the user input into discrete sentences or segments where a transaction may be implied. If multiple transactions are referenced, classify each one separately. 2. Identify Transaction Elements: - Pocket: Determine the category or label for the transaction. If not explicitly mentioned, use your best inference based on context. - Description: Provide a short label or explanation for the transaction. - Amount: Extract the numerical value of the transaction, ensuring to remove currency symbols or additional signs. - Type: Positive if the text suggests an inflow of funds; Negative if the text suggests an outflow of funds. 3. Handle Ambiguities & Missing Details: If the user does not provide a clear “pocket,” try to infer it from context (e.g., “rent,” “loan,” “food,” “transportation,” etc.). If you cannot infer a pocket from context, leave it as Unknown. If the user does not specify an amount, leave it as Unknown. If a transaction type cannot be inferred, label it as Unclear, but strive to determine Positive vs. Negative using synonyms or context clues (e.g., “gave me,” “spent,” “bought,” “earned,” “donated,” etc.). 4. Output Formatting: Structure your response in a clear format—preferably as a list or JSON for easy parsing. Ensure each transaction is captured as a separate structured entry: {'pocket':'<string>','description':'<string>','amount':'<string>','type':'<Positive|Negative>'} If multiple transactions are found, output them as an array of the above objects. 5. Error & Edge Cases: If no recognizable transactions are found in the user input, return an empty list or an indicative message. If partial information is provided, supply the known parts and use Unknown where data is missing.  Example: User Input: “I paid my electricity bill of $120 and received $50 from my friend for groceries.” Desired Output: [{'pocket':'utilities','description':'electricity bill','amount':'120','type':'Negative'},{'pocket':'groceries','description':'friend payment','amount':'50','type':'Positive'}] --- Use these instructions to parse and classify the user’s financial transactions in a consistent, accurate, and structured manner."

        json_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "Payments": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "pocket_name": {
                                        "type": "string",
                                        "enum": list_debts  # Sustituye list_debts por tu lista real
                                    },
                                    "transaction_type": {
                                        "type": "string",
                                        "enum": ["negative", "positive"]
                                    },
                                    "amount": {"type": "number"},
                                    "description": {"type": "string"}
                                },
                                "required": ["pocket_name", "transaction_type", "amount", "description"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["Payments"],
                    "additionalProperties": False
                }
            }
        }


        # Call the chat completion
        response = client.chat.completions.create(
            model="llama3.1:8b" if membership == "free" else "gpt-4o-mini",  
            messages=[
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": query
                        }
                    ]
                }
            ],
            temperature=0.2,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            response_format=json_format
        )

        # Parse the JSON result
        data = json.loads(response.choices[0].message.content)
        return data["Payments"]
