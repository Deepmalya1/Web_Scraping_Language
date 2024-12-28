# scrape_runner.py
import sys
from lexer import lexer
import ply.yacc as yacc
from parser import parser
from scraper import scrape_website

def main():
    # Ensure the user passed a file as an argument
    if len(sys.argv) < 2:
        print("Usage: python scrape_runner.py <your_custom_file.scrape>")
        sys.exit(1)
    
    # Read the file
    command_file = sys.argv[1]
    try:
        with open(command_file, 'r') as file:
            command_input = file.read().strip()
            print(f"Processing command from {command_file}...\n")

            # Parse the command input using the lexer
            lexer.input(command_input)
            for tok in lexer:
                print(tok)  # This shows how the lexer is working

            # Build and parse the command using yacc
            parsed_command = parser.parse(command_input)

            # Run the scraping logic based on parsed command
            if parsed_command:
                scrape_website(parsed_command)
            else:
                print("Failed to parse the command.")
    
    except FileNotFoundError:
        print(f"Error: The file {command_file} does not exist.")
        sys.exit(1)

if __name__ == "__main__":
    main()
