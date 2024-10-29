from openai import OpenAI
import json

class FinanceManager:
    @staticmethod
    def get(query: str, api_key : str, list_debts) -> dict:
        client = OpenAI(api_key=api_key)
        prompt = "You are a financial wizard whose expertise lies in analyzing financial transactions. When a user mentions any financial situation, your task is to identify the payments involved. Specifically, your goal is to extract the following details:\nDebt: Identify the type of debt (using the predefined list of possible debts, referenced as list_debts).\nDescription: Provide a short description of the payment.\nAmount: Extract the amount of the payment.\nType: Identify if the payment relates to a positive or negative debt."
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
                                        "enum":  list_debts
                                    },
                                    "transaction_type": {
                                        "type": "string",
                                        "enum": ["negative", "positive"]
                                    },
                                    "amount": { "type": "number" },
                                    "description": { "type": "string" }
                                },
                                "required": ["pocket_name","transaction_type", "amount", "description",  ],
                                "additionalProperties": False
                        }
                    },
                    "required": ["Payment"],
                    "additionalProperties": False
                }
            }
        }

        response = client.chat.completions.create(
        model="gpt-4o-mini",
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
        response_format= json_format
    )
        response = json.loads(response.choices[0].message.content)
        return response["Payment"]