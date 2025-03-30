import os
import streamlit as st
import json
from apify_client import ApifyClient
import openai
from langchain.memory import ConversationBufferMemory
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize APIs
APIFY_API_KEY = os.getenv('APIFY_API_KEY')
openai.api_key = os.getenv('OPENAI_API_KEY')
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

if 'memory' not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
if 'profile_data' not in st.session_state:
    st.session_state.profile_data = None
if 'job_role' not in st.session_state:
    st.session_state.job_role = None
if 'profile_analysis' not in st.session_state:
    st.session_state.profile_analysis = ""
if 'job_recommendations' not in st.session_state:
    st.session_state.job_recommendations = ""
if 'initial_analysis_done' not in st.session_state:
    st.session_state.initial_analysis_done = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

def scrape_linkedin_profile(linkedin_url: str):
    client = ApifyClient(APIFY_API_KEY)
    run_input = {"profileUrls": [linkedin_url]}
    run = client.actor("2SyF0bVxmgGr8IVCZ").call(run_input=run_input)
    profile_data = [item for item in client.dataset(run["defaultDatasetId"]).iterate_items()]
    return profile_data[0] if profile_data else {}

def analyze_profile(profile_data):
    prompt = f"""
    Analyze this LinkedIn profile:
    {json.dumps(profile_data, indent=2)}

    Provide feedback on:
    - Missing information
    - About section improvements
    - Skill gaps
    - Experience enhancements
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert LinkedIn profile optimizer."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def job_recommendation(profile_data, job_role):
    prompt = f"""
    Compare this profile:
    {json.dumps(profile_data, indent=2)}
    With {job_role} requirements.
    Provide match score, missing skills, and improvements.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a career advisor expert."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

def setup_tools():
    return [
        Tool(
            name="ScrapeLinkedInProfile",
            func=scrape_linkedin_profile,
            description="Scrape LinkedIn profile data."
        ),
        Tool(
            name="ProfileAnalysis",
            func=lambda _: st.session_state.profile_analysis,
            description="Get LinkedIn profile analysis."
        ),
        Tool(
            name="JobRecommendations",
            func=lambda _: st.session_state.job_recommendations,
            description="Get job-specific recommendations."
        )
    ]

def initialize_chat_agent():
    tools = setup_tools()
    memory = st.session_state.memory
    if st.session_state.initial_analysis_done:
        memory.chat_memory.add_user_message("Profile Analysis and Job Recommendations")
        memory.chat_memory.add_ai_message(
            f"Profile Analysis:\n{st.session_state.profile_analysis}\n\nJob Recommendations:\n{st.session_state.job_recommendations}\n"
        )
    agent = initialize_agent(
        tools,
        ChatOpenAI(model="gpt-4o", temperature=0),
        agent=AgentType.OPENAI_FUNCTIONS,
        memory=memory,
        system_message=SystemMessage(content="""
        You are a career advisor chatbot with access to profile data.
        """),
        verbose=True
    )
    return agent

def main():
    st.title("LinkedIn Career Optimizer")
    if not st.session_state.initial_analysis_done:
        with st.form("initial_inputs"):
            linkedin_url = st.text_input("LinkedIn Profile URL:")
            job_role = st.text_input("Desired Job Role:")
            if st.form_submit_button("Start Analysis"):
                if linkedin_url and job_role:
                    with st.spinner("Analyzing your profile..."):
                        try:
                            st.session_state.profile_data = scrape_linkedin_profile(linkedin_url)
                            st.session_state.job_role = job_role
                            st.session_state.profile_analysis = analyze_profile(st.session_state.profile_data)
                            st.session_state.job_recommendations = job_recommendation(st.session_state.profile_data, job_role)
                            st.session_state.initial_analysis_done = True
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error processing profile: {str(e)}")
                else:
                    st.warning("Please fill both fields")
    else:
        st.subheader("Your Analysis Results")
        st.markdown(f"**Profile Analysis:**\n{st.session_state.profile_analysis}")
        st.markdown(f"**Job Recommendations:**\n{st.session_state.job_recommendations}")
        agent = initialize_chat_agent()
        st.subheader("Career Advisor Chat")
        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])
        if prompt := st.chat_input("Ask about your profile or career options..."):
            profile_context = json.dumps(st.session_state.profile_data, indent=2) if st.session_state.profile_data else "No profile data available."
            full_prompt = f"""
            User's LinkedIn profile:
            {profile_context}
            \nUser's question:
            {prompt}
            """
            st.session_state.messages.append({"role": "user", "content": prompt})  # Store only the question in UI
            st.chat_message("user").write(prompt)  # Display only the question in UI
            with st.spinner("Processing..."):
                try:
                    response = agent.run(full_prompt)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.chat_message("assistant").write(response)
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
if __name__ == "__main__":
    main()

