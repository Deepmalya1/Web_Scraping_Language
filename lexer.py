import ply.lex as lex

# Define the tokens
tokens = (
    'SCRAPE',
    'URL',
    'INTO',
    'JSON_FILE',
    'CSV_FILE',
    'XML_FILE',
    'SELECT',
    'USER_AGENT',
    'DELAY',
    'RETRIES',
    'PROXY',
    'AUTH',
    'HEADER',
    'VALIDATE',
    'FILTER',
    'API'
)

# Regular expressions for tokens
def t_SCRAPE(t):
    r'scrape'
    return t

def t_URL(t):
    r'"[^"]+"'
    return t

def t_INTO(t):
    r'into'
    return t

def t_JSON_FILE(t):
    r'[a-zA-Z0-9_]+\.json'
    return t

def t_CSV_FILE(t):
    r'[a-zA-Z0-9_]+\.csv'
    return t

def t_XML_FILE(t):
    r'[a-zA-Z0-9_]+\.xml'
    return t

def t_SELECT(t):
    r'select'
    return t

def t_USER_AGENT(t):
    r'with_user_agent\s+"[^"]+"'
    return t

def t_DELAY(t):
    r'with_delay\s+\d+s'
    return t

def t_RETRIES(t):
    r'with_retries\s+\d+'
    return t

def t_PROXY(t):
    r'using_proxy\s+"[^"]+"'
    return t

def t_AUTH(t):
    r'using_auth\s+"[^"]+"'
    return t

def t_HEADER(t):
    r'using_headers\s+\{[^}]+\}'
    return t

def t_VALIDATE(t):
    r'validate\s+fields\s+\[[^\]]+\]'
    return t

def t_FILTER(t):
    r'filter\s+by\s+[^\s]+'
    return t

def t_API(t):
    r'using_api'
    return t

# Ignore whitespace
t_ignore = ' \t\n'

def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

if __name__ == "__main__":
    # Test the lexer
    test_input = 'scrape "https://example.com" into data.json with_user_agent "Custom UA"'
    lexer.input(test_input)
    for tok in lexer:
        print(tok)
