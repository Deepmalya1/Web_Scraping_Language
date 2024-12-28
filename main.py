# main.py
from parser import parser, ParserError
from scraper import scrape_and_save, scrape_and_save_with_selector, ScrapingError
from advanced_features import AdvancedScraper
from lexer import lexer
import sys
import os
import json
import asyncio

import requests
def print_help():
    """Print usage instructions."""
    print("""
Web Scraper Usage:
-----------------
Basic Commands:
    1. Basic scraping:
       scrape "URL" into output.json
    
    2. With selector:
       scrape "URL" select ".css-selector" into output.json
       scrape "URL" select "//xpath/selector" into output.json
    
    3. With options:
       scrape "URL" into output.json with_user_agent "Custom UA" with_delay 2s with_retries 3

Advanced Commands:
    1. Parallel scraping:
       scrape_parallel ["URL1", "URL2", "URL3"] into output.json max_concurrent 5
    
    2. Monitor changes:
       monitor "URL" interval 3600 into changes.json
    
    3. Extract structured data:
       scrape "URL" structured into output.json
    
    4. Site analysis:
       analyze "URL" into analysis.json

Output formats:
    - .json : JSON format output
    - .xml  : XML format output
    - .csv  : CSV format output

Commands:
    help    : Show this help message
    exit    : Exit the program
    clear   : Clear the screen
    status  : Show active monitors
    history : Show scraping history
    """)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def execute_command(result):
    """Execute the parsed command."""
    if not result:
        print("Invalid command: Parsing returned None")
        return
        
    try:
        advanced_scraper = AdvancedScraper()
        
        if result['type'] == 'scrape':
            if result.get('parallel'):
                # Handle parallel scraping
                urls = json.loads(result['urls'])
                max_concurrent = result.get('max_concurrent', 5)
                results = asyncio.run(advanced_scraper.parallel_scrape(urls, max_concurrent))
                
                with open(result['output_file'], 'w') as f:
                    json.dump(results, f, indent=2)
                    
            elif result.get('structured'):
                # Handle structured data extraction
                response = requests.get(result['url'])
                data = advanced_scraper.extract_structured_data(response.text)
                advanced_scraper.export_data(data, result['format'], result['output_file'])
                
            else:
                # Regular scraping
                scrape_and_save(result['url'], result['output_file'], result.get('options', {}))
                
        elif result['type'] == 'monitor':
            def change_callback(url, changes):
                print(f"\nChanges detected in {url}:")
                print(changes)
                
            thread = advanced_scraper.monitor_changes(
                result['url'],
                callback=change_callback,
                interval=result.get('interval', 3600)
            )
            print(f"Started monitoring {result['url']}")
            
        elif result['type'] == 'select':
            scrape_and_save_with_selector(
                result['url'],
                result['selector'],
                result['output_file'],
                result.get('options', {})
            )
            
        else:
            print(f"Unknown command type: {result['type']}")
            
    except ScrapingError as e:
        print(f"Scraping error: {str(e)}")
    except Exception as e:
        print(f"Error executing command: {str(e)}")

def process_input(command):
    """Process a single command."""
    command = command.strip()
    
    if not command:
        return True
        
    # Handle special commands
    if command.lower() == 'exit':
        print("Exiting...")
        return False
    elif command.lower() == 'help':
        print_help()
        return True
    elif command.lower() == 'clear':
        clear_screen()
        return True
    elif command.lower() == 'status':
        # Show active monitors
        print("Active monitors:")
        # Implement status checking
        return True
    elif command.lower() == 'history':
        # Show scraping history
        scraper = AdvancedScraper()
        # Implement history display
        return True
        
    # Parse and execute the command
    try:
        result = parser.parse(command)
        if result:
            print(f"Parsed command: {result}")
            execute_command(result)
        else:
            print("Parsing failed. Please check your command syntax.")
            print("Type 'help' for usage instructions.")
    except ParserError as e:
        print(f"Parser error: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")
        
    return True

def interactive_mode():
    """Run the scraper in interactive mode."""
    print("Web Scraper Interactive Mode")
    print("Type 'help' for usage instructions or 'exit' to quit")
    print("-" * 50)
    
    while True:
        try:
            command = input("\nEnter command > ").strip()
            if not process_input(command):
                break
        except KeyboardInterrupt:
            print("\nUse 'exit' command to quit")
        except EOFError:
            break
        except Exception as e:
            print(f"Error: {str(e)}")

def batch_mode(filename):
    """Run the scraper in batch mode, reading commands from a file."""
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith('#'):
                    print(f"\nExecuting: {line}")
                    if not process_input(line):
                        break
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found")
    except Exception as e:
        print(f"Error processing batch file: {str(e)}")

def main():
    """Main function to run the web scraper."""
    try:
        # Check if running in batch mode
        if len(sys.argv) > 1:
            if sys.argv[1] in ['-h', '--help']:
                print_help()
            else:
                batch_mode(sys.argv[1])
        else:
            interactive_mode()
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"Fatal error: {str(e)}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(main())