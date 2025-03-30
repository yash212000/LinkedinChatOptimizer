# LinkedIn Career Optimizer

## Overview
The **LinkedIn Career Optimizer** is an AI-powered chat system that helps users improve their LinkedIn profiles, analyze job fit, and receive career guidance. It extracts LinkedIn profile data, provides optimization suggestions, and generates job-specific recommendations through an interactive chat interface.

## Features
- **LinkedIn Profile Analysis**: Extracts and evaluates profile sections (About, Experience, Skills, etc.).
- **Job Fit Analysis**: Compares profiles against industry-standard job descriptions, generates match scores, and suggests improvements.
- **Interactive Chatbot**: AI-powered assistant provides career recommendations and answers user queries.
- **Memory Retention**: Tracks previous interactions for personalized responses.

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: FastAPI, LangChain, OpenAI API
- **Data Extraction**: Apify LinkedIn Scraper
- **Memory Management**: LangChain ConversationBufferMemory

## Installation
1. Clone the repository:
   ```bash
   git clone <repo-url>
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - `APIFY_API_KEY`: API key for LinkedIn scraping
   - `OPENAI_API_KEY`: API key for AI processing

## Usage
1. Run the application:
   ```bash
   streamlit run app.py
   ```
2. Enter your **LinkedIn profile URL** and **desired job role**.
3. Receive profile analysis and job fit recommendations.
4. Chat with the AI assistant for further career guidance.

## Future Enhancements
- Resume parsing for users without a LinkedIn profile.
- AI-generated cover letters.
- Job market trends analysis.
- Multilingual support.


