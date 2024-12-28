# Introduction

This project provides a flexible and customizable web scraping tool that utilizes a lexer and parser to process commands written in a custom script format (e.g., `.scrape` files). It allows users to easily scrape data from websites using simple commands.

## Features

- **Basic Scraping Commands**: Extract data from websites and save it in different formats such as JSON, CSV, or XML.
- **Customizable Options**: Include user-agent strings, set delays, specify retry attempts, and use proxies or authentication headers.
- **File-Based Command Input**: Use `.scrape` files to define scraping tasks for better readability and reusability.
- **Batch File Execution**: Run the script seamlessly using a `.bat` file for ease of use.

## Limitations

### Advanced Features Under Development

Some advanced features tagged in the documentation, such as validation, filtering, and certain API-related options, are currently in the development phase and not functional at this time. Please refrain from using these features as they may lead to unexpected behavior.

The following advanced features are still in progress:

- **`validate fields`**
- **`filter by`**
- **`using_api`**
- **`monitor`**
- **`parallel`**

These features will be fully implemented in future updates.

## Installation and Setup

### Python Setup:
1. Install Python (version 3.7 or higher).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt


#To use it OPEN
   ```bash
      console.bat
