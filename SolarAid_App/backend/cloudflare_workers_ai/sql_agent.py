import os
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

from langchain_cloudflare import ChatCloudflareWorkersAI
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.language_models import BaseChatModel


class CloudflareSQLAgent:
    """
    Reusable SQL Agent for (question(s) in natural language => SQL queries => results in text)
        - Excecuted using Cloudflare Workers AI + langchain_community's SQLDatabase.

    """

    def __init__(
        self,
        db_url: str,
        account_id: str,
        api_token: str,
        model: str = "@cf/meta/llama-3.1-8b-instruct",
        tables: Optional[List[str]] = None,
        sample_rows: int = 2,
        temperature: float = 0.0,
        max_tokens: int = 1000,
        verbose: bool = True,
    ):
        """
        Initialize the SQL Agent.

        """
        self.verbose = verbose
        self.llm = self.create_llm(model, account_id, api_token, temperature, max_tokens)
        self.db = self.create_db_connection(db_url, tables, sample_rows)
        self.dialect = self.db.dialect
        self.sql_prompt = self.get_sql_prompt()
        self.answer_prompt = self.get_answer_prompt()

        if self.verbose:
            print(f"SQL Agent initialized")
            print(f"    Database Connected: {self.dialect}")
            print(f"    Tables Found: {self.db.get_usable_table_names()}")
            print(f"    Model Used: {model}\n")

    def create_llm(
        self,
        model: str,
        account_id: str,
        api_token: str,
        temperature: float,
        max_tokens: int,
    ) -> BaseChatModel:
        """
        Create Cloudflare LLM instance.

        """
        if not account_id or not api_token:
            raise ValueError("Cloudflare account_id and api_token are required.")

        return ChatCloudflareWorkersAI(
            model=model,
            cloudflare_account_id=account_id,
            cloudflare_api_token=api_token,
            temperature=temperature,
            max_tokens=max_tokens,
            model_kwargs={"streaming": False},
        )

    def create_db_connection(
        self, db_url: str, tables: Optional[List[str]], sample_rows: int
    ) -> SQLDatabase:
        """
        Create database connection.

        """
        try:
            db_kwargs = {"sample_rows_in_table_info": sample_rows}
            if tables:
                db_kwargs["include_tables"] = tables

            return SQLDatabase.from_uri(db_url, **db_kwargs)
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def get_sql_prompt(self) -> ChatPromptTemplate:
        """
        Get SQL generation prompt template (customizable per dialect).

        """

        # PostgreSQL-specific rules
        if self.dialect == "postgresql":
            dialect_rules = f"""
            POSTGRESQL-SPECIFIC RULES:
            - Use double quotes for column and table names with capitals, e.g., "User_ID", "Donation_Amount_kWh", "User", "Donation".
            - Stick to simple queries: SELECT, JOIN, GROUP BY, ORDER BY.
            - Avoid window functions (ROW_NUMBER, RANK) and nested subqueries when possible.
            """
        else:
            dialect_rules = f"""
            DATABASE-SPECIFIC RULES:
            - Follow {self.dialect} syntax conventions
            - Use simple queries when possible"""

        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    f"""You are a {self.dialect} expert. Generate ONLY a SQL query, nothing else.

            {dialect_rules}

            GENERAL RULES:
            1. Limit results using LIMIT (default: 10) unless specified otherwise.
            2. Query only necessary columns.
            3. Do NOT perform INSERT, UPDATE, DELETE, or DROP operations.
            4. Output ONLY the SQL query, no explanations, no markdown, no extra text.

            Database Schema:
            {{schema}}""",
                ),
                ("user", "{question}"),
            ]
        )

    def get_answer_prompt(self) -> ChatPromptTemplate:
        """
        Get natural language answer generation prompt.

        """
        return ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are a helpful assistant. Convert SQL query results into answers.
                    Be concise and direct. If the results are empty, say so clearly.
                    If the user requests JSON, output strictly valid JSON with the requested fields.
                    Do not add explanations or markdown outside the JSON.""",
                ),
                (
                    "user",
                    """
                    Question: {question}
                    SQL Query Used: {sql}
                    Query Results: {results}
                    Requested Output Format: {output_format}

                    Provide the answer strictly according to the Requested Output Format. 
                    If format is 'text' or not mentioned, provide a natural language answer.
                    If format specifies JSON, output valid JSON with the requested fields and no extra text.
                """,
                ),
            ]
        )

    def clean_sql(self, sql: str) -> str:
        """
        - Remove Markdown code blocks
        - Strip leading/trailing whitespace
        """
        return sql.replace("```sql", "").replace("```", "").strip()

    def generate_sql(self, question: str) -> str:
        """
        Generate SQL query from natural language question.

        """
        schema_info = self.db.get_table_info()
        sql_chain = self.sql_prompt | self.llm

        response = sql_chain.invoke({"schema": schema_info, "question": question})

        sql = self.clean_sql(response.content)
        return sql

    def execute_sql(self, sql: str) -> str:
        """
        Execute SQL query and return results.

        """
        try:
            return self.db.run(sql)
        except Exception as e:
            raise RuntimeError(f"Query execution failed: {e}")

    def query(self, question: str, return_sql: bool = False, output_format: str = "text") -> Dict[str, Any]:
        """
        Main method: Convert natural language to SQL, execute, and return answer.

        """
        if self.verbose:
            print(f"\n{'='*70}")
            print(f"Question: {question}")
            print(f"{'='*70}")

        try:
            # Step 1: Generate SQL
            sql = self.generate_sql(question)
            if self.verbose:
                print(f"\nGenerated SQL:\n{sql}")

            # Step 2: Execute SQL
            results = self.execute_sql(sql)
            if self.verbose:
                print(f"\nQuery Results:\n{results}")

            # Step 3: Generate natural language answer / JSON formatted output
            answer_chain = self.answer_prompt | self.llm
            final_answer = answer_chain.invoke(
                {"question": question, "sql": sql, "results": results, "output_format": output_format}
            )

            response = {"answer": final_answer.content}

            if return_sql:
                response["sql"] = sql
                response["results"] = results

            if self.verbose:
                print(f"\nFinal Answer:\n{response['answer']}\n")

            return response

        except Exception as e:
            print(error_msg=str(e))

    def batch_query(self, questions: List[str]) -> List[Dict[str, Any]]:
        """
        Execute multiple queries in batch.

        """
        results = []
        for i, question in enumerate(questions, 1):
            if self.verbose:
                print(f"\n[Query {i}/{len(questions)}]")
            results.append(self.query(question))
        return results


def create_agent_from_env(
    tables: Optional[List[str]] = None, verbose: bool = True, **kwargs
) -> CloudflareSQLAgent:
    """
    Create SQL agent from environment variables.

    """
    load_dotenv()

    db_url = os.environ.get("SUPABASE_CONNECTION_URL")
    account_id = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    api_token = os.environ.get("CF_AI_API_TOKEN")

    if not db_url:
        raise ValueError("SUPABASE_CONNECTION_URL not found in environment")
    if not account_id:
        raise ValueError("CLOUDFLARE_ACCOUNT_ID not found in environment")
    if not api_token:
        raise ValueError("CF_AI_API_TOKEN not found in environment")

    return CloudflareSQLAgent(
        db_url=db_url,
        account_id=account_id,
        api_token=api_token,
        tables=tables,
        verbose=verbose,
        **kwargs,
    )


# --- Example Usage For Debugging Purposes ---
if __name__ == "__main__":
    agent = create_agent_from_env(verbose=True)

    result = agent.query(
        'Display the leaderboard ranking of users based on the "Donate_Amount" column in the "user" table.  with fields: Rank, User Name, Total Donate Amount', output_format="JSON"
    )