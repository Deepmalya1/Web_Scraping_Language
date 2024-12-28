README

Introduction

This project provides a flexible and customizable web scraping tool that utilizes a lexer and parser to process commands written in a custom script format (e.g., .scrape files). It allows users to easily scrape data from websites using simple commands.

Features

Basic Scraping Commands: Extract data from websites and save it in different formats such as JSON, CSV, or XML.

Customizable Options: Include user-agent strings, set delays, specify retry attempts, and use proxies or authentication headers.

File-Based Command Input: Use .scrape files to define scraping tasks for better readability and reusability.

Batch File Execution: Run the script seamlessly using a .bat file for ease of use.

Limitations

Advanced Features Under Development

Some advanced features tagged in the documentation, such as validation, filtering, and certain API-related options, are currently in the development phase and not functional at this time. Please refrain from using these features as they may lead to unexpected behavior.

The following advanced features are still in progress:

validate fields

filter by

using_api

These features will be fully implemented in future updates.

Installation and Setup

Python Setup:

Install Python (version 3.7 or higher).

Install dependencies:

pip install -r requirements.txt

Project Files:

Place your main.py, lexer, and parser files in the project directory.

Ensure your .scrape commands file is ready.

Batch File:

Create a .bat file to execute the program easily. Refer to the documentation for creating the batch file.

Usage

Write your commands in a .scrape file. Example:

scrape "https://example.com" into output.json with_user_agent "Mozilla/5.0" with_delay 2s

Run the batch file with the .scrape file as an argument:

scrape.bat C:\path\to\your\command.scrape

The output will be saved in the specified file format.

Contributions

Contributions to the project are welcome! Please ensure that any code related to advanced features is clearly marked as experimental in pull requests.
