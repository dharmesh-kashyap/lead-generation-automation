# Automated Lead Generation Tool

This is a **Streamlit-based application** designed to automate lead generation by scraping emails and actionable insights from URLs or Google search queries. The tool supports real-time scraping, enrichment, and interactive data management.

---

## Features

### 1. **Scraping Pipeline**
- Scrapes data from URLs or Google search queries.
- Extracts emails and relevant details.
- Enriches data with AI-generated insights using Groq API.

### 2. **User-Friendly Dashboard**
- **Interactive Table**: View, sort, filter, and select results using Ag-Grid.
- **Inline Actions**:
  - Delete or download individual entries.
- **Global Actions**:
  - Delete or download the entire table.

### 3. **Pipeline Management**
- **Run Pipeline**: Execute scraping and enrichment workflows.
- **Stop Pipeline**: Interrupt ongoing pipeline execution.

---

## Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection

### Setup Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/dharmesh-kashyap/lead-generation-automation.git
   cd Lead_scraper
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file to securely store your **Groq API Key**:
   - In the root directory of the project, create a `.env` file
   - Add the following line to the `.env` file
   ```Plaintext
    GROQ_API_KEY=your_api_key_here
   ```
4. Start th application:
   ```bash
   streamlit run dashboard.py
   ```
---

## Screenshots of the project 
- ### Dashboard
![image](https://github.com/user-attachments/assets/9730f4a6-ece5-4d73-8fae-1532f5a61a04)

- ### Testing URL
![image](https://github.com/user-attachments/assets/40edf416-cb82-4607-909d-4dd8f10a811e)

- ### Keyword Search
![image](https://github.com/user-attachments/assets/49c44c3a-fd4c-49d5-b48d-6cf00ec577e4)
![image](https://github.com/user-attachments/assets/3fa83614-13be-4a01-b2dc-660310c908f7)

--- 

## Demo video 

[streamlit-dashboard-2025-01-16-03-01-50.webm](https://github.com/user-attachments/assets/43785211-1445-4ef9-8b74-2de7524b3735)

