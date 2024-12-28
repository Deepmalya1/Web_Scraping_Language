import ply.yacc as yacc
from lexer import tokens
import json

class ParserError(Exception):
    """Custom exception for parsing errors."""
    pass

def p_statement(p):
    '''statement : scrape_statement
                | select_statement
                | api_statement'''
    p[0] = p[1]

def p_scrape_statement(p):
    '''scrape_statement : SCRAPE URL INTO output_file options'''
    try:
        url = p[2][1:-1].strip()  # Remove quotes and whitespace
        p[0] = {
            'type': 'scrape',
            'url': url,
            'output_file': p[4],
            'options': process_options(p[5])
        }
    except Exception as e:
        raise ParserError(f"Error in scrape statement: {str(e)}")

def p_select_statement(p):
    '''select_statement : SCRAPE URL SELECT selector INTO output_file options'''
    try:
        url = p[2][1:-1].strip()
        p[0] = {
            'type': 'select',
            'url': url,
            'selector': p[4],
            'output_file': p[6],
            'options': process_options(p[7])
        }
    except Exception as e:
        raise ParserError(f"Error in select statement: {str(e)}")

def p_api_statement(p):
    '''api_statement : SCRAPE URL API INTO output_file options'''
    try:
        url = p[2][1:-1].strip()
        p[0] = {
            'type': 'api',
            'url': url,
            'output_file': p[5],
            'options': process_options(p[6])
        }
    except Exception as e:
        raise ParserError(f"Error in API statement: {str(e)}")

def process_options(options):
    """Convert options list to dictionary."""
    if not options:
        return {}
        
    opts = {}
    for opt in options:
        if isinstance(opt, str):
            if opt.startswith('USER_AGENT'):
                opts['user_agent'] = opt.split('"')[1]
            elif opt.startswith('DELAY'):
                opts['delay'] = int(opt.split('s')[0].split()[-1])
            elif opt.startswith('RETRIES'):
                opts['retries'] = int(opt.split()[-1])
            elif opt.startswith('PROXY'):
                opts['proxy'] = opt.split('"')[1]
            elif opt.startswith('AUTH'):
                opts['auth'] = opt.split('"')[1]
            elif opt.startswith('HEADER'):
                # Parse header JSON
                header_str = opt.split('{')[1].split('}')[0]
                try:
                    opts['headers'] = json.loads('{' + header_str + '}')
                except json.JSONDecodeError:
                    print("Warning: Invalid header format")
    return opts

def p_output_file(p):
    '''output_file : JSON_FILE
                  | CSV_FILE
                  | XML_FILE'''
    p[0] = p[1]

def p_selector(p):
    '''selector : URL'''
    p[0] = p[1][1:-1].strip()

def p_options(p):
    '''options : option options
               | empty'''
    if len(p) == 3:
        if p[2] is None:
            p[0] = [p[1]]
        else:
            p[0] = [p[1]] + p[2]
    else:
        p[0] = None

def p_option(p):
    '''option : USER_AGENT
             | DELAY
             | RETRIES
             | PROXY
             | AUTH
             | HEADER
             | VALIDATE
             | FILTER'''
    p[0] = p[1]

def p_empty(p):
    '''empty :'''
    pass

def p_error(p):
    if p:
        print(f"Syntax error at '{p.value}'")
    else:
        print("Syntax error at EOF")

# Create the parser
parser = yacc.yacc()

if __name__ == "__main__":
    # Test the parser
    test_input = 'scrape "https://example.com" into data.json with_user_agent "Custom UA"'
    result = parser.parse(test_input)
    print(result)
