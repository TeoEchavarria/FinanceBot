# FinanceBot

[![Telegram](https://img.shields.io/badge/Telegram-FinanceTeoBot-blue)](https://t.me/finance_teobot)

**FinanceBot** is an advanced Telegram bot designed to help you manage your personal finances efficiently using natural language processing. The bot leverages **OpenAI** for Pro members, offering sophisticated financial analysis capabilities, and **Ollama** for Free users, providing a local and cost-free solution for processing natural language.

## 🔧 Technologies Used

- **Programming Language**: Python
- **Telegram Integration**: [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- **Data Validation**: [Pydantic v2](https://pydantic-docs.helpmanual.io/)
- **Database**: [Supabase](https://supabase.com/) for storing user data and transactions
- **AI Models**:
  - **OpenAI API**: Used by Pro members for advanced financial processing.
  - **Ollama**: Implemented for Free users, allowing local processing of natural language without API costs.
- **Containerization**: [Docker](https://www.docker.com/) for easy and scalable deployment
- **Voice Processing**: Custom voice-to-text service integrated with the bot

## 📋 Main Features

- **Financial Pockets Management**: Create and manage multiple pockets (financial categories) to organize your finances.
  
- **Register Transactions via Natural Language**: Record money inflows and outflows using text commands or voice notes.
  
- **Support for Free and Pro Users**: Depending on your membership, the bot utilizes Ollama or OpenAI to process your requests.

## 📲 Telegram Bot

Start managing your finances easily and naturally!

[👉 FinanceTeoBot on Telegram](https://t.me/finance_teobot)

## Project Structure

- **src/**  
  - **config/**: Configuration files for the project ([config.py](src/config/config.py), [openai_config.py](src/config/openai_config.py)).
  - **data/**: Contains the start-up message ([start.md](src/data/start.md)).
  - **handlers/**: Telegram command and message handlers (e.g., [start_handler.py](src/handlers/start_handler.py), [talk_handler.py](src/handlers/talk_handler.py), [create_pocket_handler.py](src/handlers/create_pocket_handler.py), [get_pockets_handler.py](src/handlers/get_pockets_handler.py)).
  - **models/**: Pydantic models representing the database objects (e.g., [user.py](src/models/user.py), [pocket.py](src/models/pocket.py), [purchase.py](src/models/purchase.py)).
  - **scripts/**: Shell scripts for deployment ([deploy.sh](src/scripts/deploy.sh), [setup.sh](src/scripts/setup.sh)).
  - **services/**: Business logic and database interactions, including financial queries and voice-to-text processing (e.g., [finance_manager/query_service.py](src/services/finance_manager/query_service.py), [voice_to_text.py](src/services/voice_to_text.py)).
  - **utils/**: Utility functions for logging, decorators, serialization, and context management.

## Environment Variables

Before running the project, you must set the following environment variables:
- **TELEGRAM_TOKEN**: Your Telegram bot token.
- **SUPABASE_URL**: The URL for your Supabase instance.
- **SUPABASE_KEY**: The API key for connecting to Supabase.
- **OPENAI_API_KEY**: API key for OpenAI (used by Pro users).  
  _(For Free users, the bot connects to a local Ollama instance.)_

It is recommended to create a `.env` file in the root of the repository to store these variables.

## Running with Docker

The repository includes a [Dockerfile](Dockerfile) and an [entrypoint.sh](entrypoint.sh) script to containerize the application.

### Build the Docker Image

Run the following command in the repository root:

```sh
docker build -t finance-bot .

docker run --env-file .env -p 8000:8000 finance-bot
```