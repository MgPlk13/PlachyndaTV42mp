BLOCKED_COMMANDS = [
    "DROP",
    "TRUNCATE",
    "INSERT",
    "UPDATE",
    "DELETE",
    "ALTER",
    "GRANT",
    "REVOKE",
    "CREATE",
]

BLOCKED_TOKENS = [
    "UNION",
    "--",
    ";--",
    ";",
    "/*",
    "*/",
]
