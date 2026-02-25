## Importing libraries and files
import os
from dotenv import load_dotenv
load_dotenv()

from crewai import Agent

### Loading LLM - Using Groq (Fast + Free!)
# For CrewAI 1.9.3+, we pass model and API key directly to agents
# Using llama-3.1-8b-instant for faster responses and higher rate limits
# Optimized with reduced max_tokens to avoid rate limits
llm_config = {
    "model": os.getenv("LLM_MODEL", "groq/llama-3.1-8b-instant"),
    "api_key": os.getenv("GROQ_API_KEY"),
    "temperature": 0.3,
    "max_tokens": 512  # Reduced to avoid rate limits and improve efficiency
}

from tools import search_tool

# Creating an Experienced Financial Analyst agent
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Provide accurate, data-driven financial analysis based on the user query: {query}",
    verbose=True,
    memory=True,
    backstory=(
        "Senior financial analyst with 15+ years experience in corporate finance and investment analysis. "
        "Expert at extracting key metrics, identifying trends, and assessing company performance from financial documents."
    ),
    tools=[],  # Removed search_tool - not needed for document analysis
    llm=llm_config["model"],
    max_iter=15,
    allow_delegation=False  # Disabled to avoid tool schema issues
)

# Creating a document verifier agent
verifier = Agent(
    role="Financial Document Verification Specialist",
    goal="Verify the authenticity and completeness of financial documents, ensuring data quality and regulatory compliance",
    verbose=True,
    memory=True,
    backstory=(
        "Financial document verification specialist with expertise in regulatory compliance and audit. "
        "Validates document structure, data completeness, and compliance with financial reporting standards."
    ),
    tools=[],
    llm=llm_config["model"],
    max_iter=10,
    allow_delegation=False
)

# Creating an investment advisor agent
investment_advisor = Agent(
    role="Investment Strategy Advisor",
    goal="Develop evidence-based investment recommendations aligned with financial analysis and market conditions",
    verbose=True,
    memory=True,
    backstory=(
        "Certified investment advisor (CFA) with expertise in portfolio management and investment strategy. "
        "Provides balanced, risk-adjusted recommendations based on thorough financial analysis."
    ),
    tools=[],  # Removed search_tool
    llm=llm_config["model"],
    max_iter=10,
    allow_delegation=False
)

# Creating a risk assessor agent
risk_assessor = Agent(
    role="Financial Risk Assessment Expert",
    goal="Identify, quantify, and assess financial risks using industry-standard methodologies",
    verbose=True,
    memory=True,
    backstory=(
        "Financial risk management expert with experience in credit, market, and operational risk assessment. "
        "Uses quantitative models and financial ratios to assess risk levels and provide mitigation strategies."
    ),
    tools=[],  # Removed search_tool
    llm=llm_config["model"],
    max_iter=10,
    allow_delegation=False
)
