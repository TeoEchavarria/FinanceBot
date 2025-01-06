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

        prompt = (
            "You are a financial wizard whose expertise lies in analyzing "
            "financial transactions. When a user mentions any financial situation, "
            "your task is to identify the payments involved. Specifically, your goal "
            "is to extract the following details:\n"
            "Debt: Identify the type of debt (using the predefined list of possible debts, "
            "referenced as list_debts).\n"
            "Description: Provide a short description of the payment.\n"
            "Amount: Extract the amount of the payment.\n"
            "Type: Identify if the payment relates to a positive or negative debt."
        )

        json_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "response",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "Payment": {
                            "type": "object",
                            "properties": {
                                "pocket_name": {
                                    "type": "string",
                                    "enum": list_debts
                                },
                                "transaction_type": {
                                    "type": "string",
                                    "enum": ["negative", "positive"]
                                },
                                "amount": {"type": "number"},
                                "description": {"type": "string"}
                            },
                            "required": ["pocket_name","transaction_type","amount","description"],
                            "additionalProperties": False
                        }
                    },
                    "required": ["Payment"],
                    "additionalProperties": False
                }
            }
        }

        # Call the chat completion
        response = client.chat.completions.create(
            model="llama3.2:3b" if membership == "free" else "gpt-4o-mini",  
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
        return data["Payment"]
