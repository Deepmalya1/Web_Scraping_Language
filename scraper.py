# scraper.py
import os
import requests
import json
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

class ScrapingError(Exception):
    """Custom exception for scraping errors."""
    pass

def validate_url(url):
    """Validate URL format and accessibility."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False

def create_directory_if_not_exists(file_path):
    """Create directory for output file if it doesn't exist."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

def scrape_and_save(url, output_file, options=None):
    """
    Scrape content from URL and save to file with specified options.
    """
    if not options:
        options = {}

    if not validate_url(url):
        raise ScrapingError(f"Invalid URL: {url}")

    # Setup headers
    headers = {
        'User-Agent': options.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    }
    headers.update(options.get('headers', {}))

    # Setup proxy if provided
    proxies = {}
    if options.get('proxy'):
        proxies = {
            'http': options['proxy'],
            'https': options['proxy']
        }

    # Handle retries
    max_retries = options.get('retries', 3)
    delay = options.get('delay', 0)

    for attempt in range(max_retries):
        try:
            if delay and attempt > 0:
                time.sleep(delay)

            response = requests.get(
                url, 
                headers=headers, 
                proxies=proxies,
                timeout=30,
                auth=tuple(options['auth'].split(':')) if options.get('auth') else None
            )
            response.raise_for_status()

            # Create output directory if needed
            create_directory_if_not_exists(output_file)

            # Handle different output formats
            extension = os.path.splitext(output_file)[1].lower()
            
            if extension == '.json':
                output_data = {
                    "url": url,
                    "status": response.status_code,
                    "content": response.text,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "headers": dict(response.headers)
                }
                with open(output_file, 'w', encoding='utf-8') as file:
                    json.dump(output_data, file, indent=2)
                    
            elif extension == '.xml':
                # Basic XML wrapper for the content
                xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
                <scrape>
                    <url>{url}</url>
                    <timestamp>{time.strftime("%Y-%m-%d %H:%M:%S")}</timestamp>
                    <content><![CDATA[{response.text}]]></content>
                </scrape>"""
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(xml_content)
                    
            elif extension == '.csv':
                # Basic CSV with metadata
                with open(output_file, 'w', encoding='utf-8') as file:
                    file.write(f"URL,Timestamp,Content\n")
                    file.write(f"{url},{time.strftime('%Y-%m-%d %H:%M:%S')},{response.text}")

            print(f"Successfully scraped {url} and saved to {output_file}")
            return

        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise ScrapingError(f"Failed to scrape {url} after {max_retries} attempts: {str(e)}")
            print(f"Attempt {attempt + 1} failed, retrying...")

def scrape_and_save_with_selector(url, selector, output_file, options=None):
    """
    Scrape content using CSS/XPath selector and save to file.
    """
    if not options:
        options = {}

    try:
        response = requests.get(
            url, 
            headers={'User-Agent': options.get('user_agent', 'Mozilla/5.0')},
            proxies={'http': options.get('proxy'), 'https': options.get('proxy')} if options.get('proxy') else None,
            auth=tuple(options['auth'].split(':')) if options.get('auth') else None
        )
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Handle both CSS and XPath selectors
        if selector.startswith('//'):  # XPath
            from lxml import etree
            tree = etree.HTML(response.text)
            elements = tree.xpath(selector)
            results = [etree.tostring(el, encoding='unicode') for el in elements]
        else:  # CSS
            elements = soup.select(selector)
            results = [str(el) for el in elements]

        # Save results
        create_directory_if_not_exists(output_file)
        
        # Handle different output formats
        extension = os.path.splitext(output_file)[1].lower()
        
        if extension == '.json':
            with open(output_file, 'w', encoding='utf-8') as file:
                json.dump({
                    "url": url,
                    "selector": selector,
                    "results": results,
                    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
                }, file, indent=2)
                
        elif extension == '.xml':
            xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
            <scrape>
                <url>{url}</url>
                <selector>{selector}</selector>
                <timestamp>{time.strftime("%Y-%m-%d %H:%M:%S")}</timestamp>
                <results>
                    {''.join(f'<result><![CDATA[{result}]]></result>' for result in results)}
                </results>
            </scrape>"""
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(xml_content)
                
        elif extension == '.csv':
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(f"URL,Selector,Result\n")
                for result in results:
                    file.write(f"{url},{selector},{result}\n")

        print(f"Successfully scraped {url} with selector '{selector}' and saved to {output_file}")

    except Exception as e:
        raise ScrapingError(f"Failed to scrape {url} with selector '{selector}': {str(e)}")

if __name__ == "__main__":
    # Test code
    test_url = "https://example.com"
    test_output = "test_output.json"
    test_options = {
        "user_agent": "Custom User Agent",
        "retries": 3,
        "delay": 1
    }
    
    try:
        scrape_and_save(test_url, test_output, test_options)
    except ScrapingError as e:
        print(f"Scraping error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")