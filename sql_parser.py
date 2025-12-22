import re

import sqlparse
from sqlparse.tokens import Keyword, Comment

from rule_checker import BLOCKED_COMMANDS, BLOCKED_TOKENS


def clean_token(value: str) -> str:
    return re.sub(r"[;(),]", "", value).strip().upper()


class SQLRuleParser:
    def __init__(self):
        self.blocked_commands = set(BLOCKED_COMMANDS)
        self.blocked_tokens = set(BLOCKED_TOKENS)

    def is_safe(self, sql: str) -> bool:
        result, _ = self.check_query(sql)
        return result

    def check_query(self, sql: str):
        try:
            parsed = sqlparse.parse(sql)
            if not parsed:
                return False, "Empty or invalid SQL"

            stmt = parsed[0]

            first_token = stmt.token_first(skip_cm=True)
            if first_token is None:
                return False, "No first token"

            first_value = clean_token(first_token.value)
            if first_value in self.blocked_commands:
                return False, f"Blocked command: {first_value}"

            for token in stmt.flatten():
                if token.ttype in (Keyword, Comment):
                    value = clean_token(token.value)
                    if value in self.blocked_tokens:
                        return False, f"Blocked token: {value}"

            return True, "Safe"

        except Exception as e:
            return False, f"Error parsing SQL: {e}"
