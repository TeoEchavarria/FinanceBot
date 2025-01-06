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
