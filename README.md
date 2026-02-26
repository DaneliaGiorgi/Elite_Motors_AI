# Elite Motors AI Agent

An intelligent, enterprise-grade AI assistant built with **LangGraph**, **Gemini 2.0 Flash**, and **PostgreSQL**.

## Key Features
- **Dynamic RBAC (Role-Based Access Control):** The agent identifies user roles (Admin/Manager) and restricts database actions (e.g., only Admins can DELETE or UPDATE records).
- **Stric Data Collection & Validation:** Integrated **Pydantic** models to ensure every vehicle entry (Year, Price, Mileage) follows strict business logic.
- **Audit Logging System:** A built-in `ShowroomLogger` records every AI tool call, SQL query, and response in `src/showroom.log` for security auditing.
- **Universal Multi-language Support:** Automatically detects user language and responds in the same script (e.g., Georgian Script for Georgian users).
- **Stateful Conversational Memory:** Uses LangGraph's `MemorySaver` to remember user context and handle corrections during data entry.

## Tech Stack
- **AI Framework:** LangChain / LangGraph
- **LLM:** Google Gemini 2.0 Flash
- **Database:** PostgreSQL (SQLAlchemy / Psycopg2)
- **Validation:** Pydantic v2
- **Environment:** Python 3.x / Dotenv

## Quick Start

1. **Clone & Install**:
   ```bash
   git clone [https://github.com/DaneliaGiorgi/Elite_Motors_AI.git](https://github.com/DaneliaGiorgi/Elite_Motors_AI.git)
   cd Elite_Motors_AI
   pip install -r requirements.txt