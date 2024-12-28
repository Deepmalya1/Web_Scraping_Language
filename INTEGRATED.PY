import ply.lex as lex
import ply.yacc as yacc
import requests
import json

# Lexer definitions
tokens = (
    'SCRAPE',      # 'scrape' keyword
    'URL',         # URL enclosed in double quotes
    'INTO',        # 'into' keyword
    'JSON_FILE'    # JSON file names
)

# Regular expressions for tokens
t_SCRAPE = r'scrape'
t_URL = r'"[^"]+"'  # Matches strings in double quotes (URLs)
t_INTO = r'into'
t_JSON_FILE = r'[a-zA-Z0-9_\.]+\.json'  # Matches file names ending with .json

# Ignoring whitespace and tabs
t_ignore = ' \t'

# Error handling for lexer
def t_error(t):
    print(f"Illegal character '{t.value[0]}'")
    t.lexer.skip(1)

# Create lexer
lexer = lex.lex()

# Parser definitions
def p_statement_scrape(p):
    'statement : SCRAPE URL INTO JSON_FILE'
    url = p[2][1:-1]  # Remove quotes from URL
    json_file = p[4]
    print(f"Scraping URL: {url} into file: {json_file}")
    
    # Scrape the data and save to a JSON file
    scrape_and_save(url, json_file)
    p[0] = {'url': url, 'json_file': json_file}

def p_error(p):
    print("Syntax error in input!")

def scrape_and_save(url, json_file):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            with open(json_file, 'w') as file:
                json.dump({"content": response.text}, file)
            print(f"Data scraped and saved to {json_file}")
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")

# Create the parser
parser = yacc.yacc()

# Main function to interact with the user
def main():
    command = input("Enter your command: ")
    result = parser.parse(command)
    if result:
        print(f"Parsed result: {result}")

if __name__ == "__main__":
    main()
