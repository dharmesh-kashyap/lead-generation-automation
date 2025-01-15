import sqlite3
import requests
from bs4 import BeautifulSoup
import random
import time
from groq import Groq
import pandas as pd
import re
import os
from dotenv import load_dotenv
import streamlit as st

GROQ_API_KEY = st.secrets["GROQ_API_KEY"]

# Set your Groq API key
client = Groq(api_key=GROQ_API_KEY)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

# Regex for email extraction
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Scraping function for Google search or URLs
def scrape_google_search(input_text):
    """
    Scrapes Google search results or emails from URLs.

    Args:
        input_text (str): Either a Google search query or a URL.

    Returns:
        list[dict]: List of dictionaries containing emails and relevant details.
    """
    query = input_text.strip()
    is_url = query.startswith("http")  # Detect if input is a URL

    if is_url:
        try:
            print(f"Scraping URL: {query}")
            emails = extract_emails_from_url(query)
            return [{"query": query, "title": "Scraped from URL", "url": query, "description": f"Emails: {', '.join(emails)}", "emails": emails}]
        except Exception as e:
            print(f"Error scraping URL: {e}")
            return []

    else:
        try:
            print(f"Scraping Google Search for: {query}")
            url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            headers = {"User-Agent": random.choice(USER_AGENTS)}
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            search_results = []

            for result in soup.select(".tF2Cxc"):
                title = result.select_one(".DKV0Md").text if result.select_one(".DKV0Md") else "No Title"
                link = result.select_one(".yuRUbf a")["href"] if result.select_one(".yuRUbf a") else "No Link"
                description = result.select_one(".VwiC3b").text if result.select_one(".VwiC3b") else "No Description"
                emails = extract_emails_from_url(link)
                search_results.append({"query": query, "title": title, "url": link, "description": description, "emails": emails})

            return search_results

        except Exception as e:
            print(f"Error scraping Google Search: {e}")
            return []


def extract_emails_from_url(url, max_links=10):
    """
    Extracts emails from the given URL and its linked pages.

    Args:
        url (str): URL to scrape for emails.
        max_links (int): Maximum number of linked pages to process.

    Returns:
        list: List of unique emails found.
    """
    try:
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        response = requests.get(url, headers=headers, timeout=10)  # Timeout added
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        emails = list(set(re.findall(EMAIL_REGEX, response.text)))  # Emails from the main page

        # Process a limited number of linked pages
        links = soup.find_all('a', href=True)[:max_links]
        for link in links:
            href = link["href"]
            if href.startswith("http"):
                try:
                    response = requests.get(href, headers=headers, timeout=10)  # Timeout added
                    emails.extend(re.findall(EMAIL_REGEX, response.text))
                except Exception:
                    continue  # Skip problematic links

        return list(set(emails))  # Return unique emails
    except Exception as e:
        print(f"Error extracting emails from {url}: {e}")
        return []



# Enrichment function using Groq
def enrich_with_groq(scraped_data):
    """
    Enriches the scraped data using Groq for actionable insights.

    Args:
        scraped_data (list[dict]): List of scraped data dictionaries.

    Returns:
        list[dict]: Enriched data with AI-generated insights.
    """
    enriched_data = []
    for record in scraped_data:
        title = record.get("title", "No title available")
        description = record.get("description", "No description available")
        url = record.get("url", "N/A")

        retry_attempts = 3
        while retry_attempts > 0:
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": f"Analyze the following data and provide actionable insights:\n"
                                       f"Title: {title}\nDescription: {description}\nURL: {url}"
                        }
                    ],
                    model="gemma2-9b-it",
                )
                insights = chat_completion.choices[0].message.content.strip()
                record["ai_insights"] = insights

                if description == "No description available":
                    record["description"] = insights.split("\n")[0]
                break  # Exit retry loop on success
            except Exception as e:
                print(f"Error enriching data with Groq: {e}")
                retry_attempts -= 1
                time.sleep(5)  # Wait before retrying
                if retry_attempts == 0:
                    record["ai_insights"] = "Unable to generate insights."

        enriched_data.append(record)

    return enriched_data


# Save data to SQLite
def save_to_database(data):
    """
    Saves data into the SQLite database.

    Args:
        data (list[dict]): Data to be saved into the database.
    """
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()

        # Ensure the table exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                title TEXT,
                url TEXT,
                description TEXT,
                ai_insights TEXT,
                emails TEXT
            )
        """)

        # Insert each record into the table
        for record in data:
            query = record.get("query", "N/A")
            title = record.get("title", "N/A")
            url = record.get("url", "N/A")
            description = record.get("description", "N/A")
            ai_insights = record.get("ai_insights", "N/A")
            emails = ", ".join(record.get("emails", []))

            cursor.execute("""
                INSERT INTO leads (query, title, url, description, ai_insights, emails)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (query, title, url, description, ai_insights, emails))

        conn.commit()

    except sqlite3.Error as e:
        print(f"Database error: {e}")

    finally:
        conn.close()


# Fetch data from SQLite
def fetch_from_database():
    """
    Fetches all data from the SQLite database.

    Returns:
        pd.DataFrame: DataFrame containing all saved leads.
    """
    try:
        conn = sqlite3.connect("leads.db")
        query = "SELECT * FROM leads ORDER BY id DESC"  # Latest results at the top
        df = pd.read_sql_query(query, conn)  # Return as Pandas DataFrame
        return df

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return pd.DataFrame()

    finally:
        conn.close()


# Delete all data from SQLite
def delete_all_data():
    """
    Deletes all data from the SQLite database.
    """
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


# Delete a single entry from SQLite
def delete_single_entry(entry_id):
    """
    Deletes a single entry from the SQLite database.

    Args:
        entry_id (int): ID of the entry to delete.
    """
    try:
        conn = sqlite3.connect("leads.db")
        cursor = conn.cursor()
        cursor.execute("DELETE FROM leads WHERE id = ?", (entry_id,))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
