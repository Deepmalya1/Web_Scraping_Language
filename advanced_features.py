# advanced_features.py
import asyncio
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
import json
import sqlite3
import hashlib
from datetime import datetime
import logging
from urllib.parse import urljoin
import xml.etree.ElementTree as ET
import threading
from queue import Queue
import time
from difflib import unified_diff

class AdvancedScraper:
    def __init__(self, db_path="scraper.db"):
        self.db_path = db_path
        self.setup_database()
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(
            filename='scraper.log',
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def setup_database(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS snapshots 
                    (url TEXT, content_hash TEXT, content TEXT, 
                     timestamp TEXT, changes TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS scrape_history
                    (url TEXT, timestamp TEXT, success INTEGER, error TEXT)''')
        conn.commit()
        conn.close()

    async def parallel_scrape(self, urls, max_concurrent=5):
        """Scrape multiple URLs in parallel."""
        async with aiohttp.ClientSession() as session:
            tasks = []
            sem = asyncio.Semaphore(max_concurrent)
            
            async def fetch_with_semaphore(url):
                async with sem:
                    try:
                        async with session.get(url) as response:
                            return {'url': url, 'content': await response.text(), 'status': response.status}
                    except Exception as e:
                        return {'url': url, 'error': str(e)}

            for url in urls:
                task = asyncio.create_task(fetch_with_semaphore(url))
                tasks.append(task)

            return await asyncio.gather(*tasks)

    def monitor_changes(self, url, callback=None, interval=3600):
        """Monitor a URL for changes."""
        def get_content_hash(content):
            return hashlib.md5(content.encode()).hexdigest()

        def monitor_task():
            while True:
                try:
                    async def fetch():
                        async with aiohttp.ClientSession() as session:
                            async with session.get(url) as response:
                                return await response.text()

                    content = asyncio.run(fetch())
                    content_hash = get_content_hash(content)

                    conn = sqlite3.connect(self.db_path)
                    c = conn.cursor()
                    
                    # Get last snapshot
                    c.execute("SELECT content FROM snapshots WHERE url=? ORDER BY timestamp DESC LIMIT 1", (url,))
                    last_snapshot = c.fetchone()

                    if last_snapshot and content != last_snapshot[0]:
                        diff = list(unified_diff(last_snapshot[0].splitlines(), content.splitlines()))
                        diff_text = '\n'.join(diff)
                        
                        c.execute("""INSERT INTO snapshots 
                                   (url, content_hash, content, timestamp, changes)
                                   VALUES (?, ?, ?, ?, ?)""",
                                (url, content_hash, content, datetime.now().isoformat(), diff_text))
                        
                        if callback:
                            callback(url, diff_text)
                        
                    elif not last_snapshot:
                        c.execute("""INSERT INTO snapshots 
                                   (url, content_hash, content, timestamp, changes)
                                   VALUES (?, ?, ?, ?, ?)""",
                                (url, content_hash, content, datetime.now().isoformat(), None))

                    conn.commit()
                    conn.close()

                except Exception as e:
                    logging.error(f"Error monitoring {url}: {str(e)}")

                time.sleep(interval)

        thread = threading.Thread(target=monitor_task, daemon=True)
        thread.start()
        return thread

    def extract_structured_data(self, html_content):
        """Extract structured data from HTML."""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        structured_data = {
            'title': soup.title.string if soup.title else None,
            'meta_tags': {},
            'links': [],
            'images': [],
            'structured_data': []
        }

        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property'))
            content = meta.get('content')
            if name and content:
                structured_data['meta_tags'][name] = content

        # Links
        for link in soup.find_all('a', href=True):
            structured_data['links'].append({
                'text': link.get_text(strip=True),
                'href': link['href'],
                'title': link.get('title')
            })

        # Images
        for img in soup.find_all('img', src=True):
            structured_data['images'].append({
                'src': img['src'],
                'alt': img.get('alt', ''),
                'title': img.get('title')
            })

        # Schema.org data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                structured_data['structured_data'].append(json.loads(script.string))
            except json.JSONDecodeError:
                continue

        return structured_data

    def export_data(self, data, format_type, output_file):
        """Export data to various formats."""
        if format_type == 'json':
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format_type == 'csv':
            # Flatten the data structure
            flat_data = pd.json_normalize(data)
            flat_data.to_csv(output_file, index=False, encoding='utf-8')
        
        elif format_type == 'xml':
            root = ET.Element("data")
            
            def dict_to_xml(d, parent):
                for key, value in d.items():
                    child = ET.SubElement(parent, str(key))
                    if isinstance(value, dict):
                        dict_to_xml(value, child)
                    elif isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                dict_to_xml(item, ET.SubElement(child, "item"))
                            else:
                                ET.SubElement(child, "item").text = str(item)
                    else:
                        child.text = str(value)

            dict_to_xml(data, root)
            tree = ET.ElementTree(root)
            tree.write(output_file, encoding='utf-8', xml_declaration=True)