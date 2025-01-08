import json, os
from openai import OpenAI
from services.finance_manager.consult_service import query_finances

from utils.logger import LoggingUtil

logger = LoggingUtil.setup_logger()

def process_finance_query(user_query: str, list_debts, membership: str, user_id) -> dict:
    # Initialize the OpenAI client
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

    # Define the tool
    tools = [
        {
            "type": "function",
            "function": {
                "name": "query_finances",
                "description": "Perform finance-related queries on pockets and purchases",
                "strict": True,
                "parameters": {
                    "type": "object",
                    "properties": {
                    "query_type": {
                        "type": "string",
                        "enum": [
                            "list_pockets",
                            "pocket_balance",
                            "pocket_expenses",
                            "compare_balance",
                            "sum_purchases",
                            "average_purchase_amount"
                        ]
                    },
                    "pocket_name": {
                        "type": "string",
                        "enum": list_debts
                    },
                    "amount": {
                        "type": "number",
                        "description": "A numerical amount to compare with or to use in calculations."
                    },
                    "time_range": {
                        "type": "string",
                        "enum": [
                            "last month",
                            "last 6 months",
                            "all time"
                        ]
                    }
                    },
                    "additionalProperties": False,
                    "required": [
                        "query_type",
                        "pocket_name",
                        "amount",
                        "time_range"
                    ]
                }
                },
        }
    ]

    messages = [
            {
                "role": "system",
                "content": (
                    "You are a financial assistant designed to help users manage and analyze their finances by querying pockets and purchases. Using the `query_finances` tool, you perform tasks such as listing pockets, checking pocket balances, reviewing expenses, comparing balances, and calculating totals or averages for purchases within specified timeframes. Users provide a query type (e.g., `list_pockets`, `pocket_balance`, `pocket_expenses`, `compare_balance`, `sum_purchases`, or `average_purchase_amount`), along with optional details like pocket name, time range (`last month`, `last 6 months`, `all time`), or a numerical amount for comparisons or calculations. When a user asks a question, map their request to the appropriate query type and parameters, ensuring accurate and clear responses. For example, if a user asks, What is the balance of my 'Savings' pocket? the tool should execute a `pocket_balance` query with the pocket name specified. If they request, Compare my 'Emergency' pocket to 3,000,000, it should execute a `compare_balance` query with both the pocket name and amount. Provide responses in a user-friendly manner, such as The balance of the 'Savings' pocket is 1,250,000 or Your total expenses in the 'Travel' pocket for the last 6 months are 780,000."
                ),
            },
            {
                "role": "user",
                "content": user_query,
            },
        ]

    # Start the chat completion with a system prompt and the user's query
    response_message = client.chat.completions.create(
        model="llama3.1:8b" if membership == "free" else "gpt-4o-mini", 
        messages=messages,
        tools=tools,
    )
    # Step 2: Determine if the response from the model includes a tool call.
    tool_calls = response_message.choices[0].message.tool_calls
    if tool_calls:
        # Extract tool call details
        tool_call_id = tool_calls[0].id
        tool_function_name = tool_calls[0].function.name
        function_arguments = tool_calls[0].function.arguments

        try:
            args = json.loads(function_arguments)
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding arguments: {e}")
            args = None

        # Step 3: Call the function and retrieve results
        if args is not None:
            if tool_function_name == 'query_finances':
                # Call the local query_finances function with parsed arguments
                result = query_finances(
                    query_type=args.get("query_type"),
                    pocket_name=args.get("pocket_name"),
                    amount=args.get("amount"),
                    time_range=args.get("time_range"),
                    user_id=user_id 
                )

                # Append the tool response to the messages list
                messages.append({
                    "role": "system",
                    "tool_call_id": tool_call_id,
                    "name": tool_function_name,
                    "content": json.dumps(result)
                })

                # Step 4: Invoke the chat completions API with the function response appended to the messages list
                model_response_with_function_call = client.chat.completions.create(
                    model="gpt-4o",
                    messages=messages,
                )
                return model_response_with_function_call.choices[0].message.content
            else:
                logger.error(f"Error: function {tool_function_name} does not exist")
    else:
        # If no function call was identified, return the content directly.
        return response_message.content
