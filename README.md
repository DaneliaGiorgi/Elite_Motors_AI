# Elite Motors AI Agent

An intelligent, role-based AI assistant built with **LangChain**, **Gemini 2.0 Flash**, and **PostgreSQL**.

## Key Features
- **Dynamic RBAC (Role-Based Access Control):** The agent identifies user roles (Admin/Manager) and restricts database actions accordingly.
- **Universal Multi-language Support:** Automatically detects user language and translates database outputs (Brand, Price, etc.) on the fly.
- **SQL Agent Integration:** Uses LangChain's SQL toolkit to reason and query data safely.
- **Modern Architecture:** Clean separation of concerns between Factory, Main, and Database layers.

## Tech Stack
- **AI Framework:** LangChain
- **LLM:** Google Gemini 2.0 Flash
- **Database:** PostgreSQL (SQLAlchemy)
- **Environment:** Python 3.x / Dotenv