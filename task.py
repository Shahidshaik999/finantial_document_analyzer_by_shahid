## Importing libraries and files
from crewai import Task
from agents import financial_analyst, verifier, investment_advisor, risk_assessor
from tools import search_tool

## Creating a task to analyze financial documents
analyze_financial_document = Task(
    description=(
        "Analyze financial document for query: {query}\n\n"
        "Document:\n{document_content}\n\n"
        "Extract:\n"
        "1. Key metrics (revenue, margins, cash flow, debt)\n"
        "2. Financial trends\n"
        "3. Company health\n"
        "4. Specific insights for query"
    ),
    expected_output=(
        "Financial Analysis:\n\n"
        "## Key Metrics\n"
        "- Revenue, margins, cash flow, debt\n\n"
        "## Financial Health\n"
        "- Overall position and trends\n\n"
        "## Insights\n"
        "- 3-5 data-backed findings"
    ),
    agent=financial_analyst,
    tools=[],  # No external tools needed
    async_execution=False,
)

## Creating a document verification task
verification_task = Task(
    description=(
        "Verify document quality and completeness.\n\n"
        "Document:\n{document_content}\n\n"
        "Check:\n"
        "1. Document type (10-K, 10-Q, earnings)\n"
        "2. Required statements present\n"
        "3. Data quality issues"
    ),
    expected_output=(
        "Verification Report:\n\n"
        "## Document Type\n"
        "- Classification and period\n\n"
        "## Completeness\n"
        "- ✓/✗ Required statements\n\n"
        "## Quality\n"
        "- Issues found (if any)\n"
        "- Status: VERIFIED or ISSUES"
    ),
    agent=verifier,
    tools=[],
    async_execution=False,
)

## Creating an investment analysis task
investment_analysis_task = Task(
    description=(
        "Provide investment recommendation based on analysis.\n\n"
        "Context: {query}\n\n"
        "Assess:\n"
        "1. Investment potential\n"
        "2. Valuation metrics\n"
        "3. Key risks and opportunities\n"
        "4. Clear recommendation"
    ),
    expected_output=(
        "Investment Analysis:\n\n"
        "## Recommendation\n"
        "- Buy/Hold/Sell with rationale\n\n"
        "## Strengths\n"
        "- 3 key positives\n\n"
        "## Risks\n"
        "- 3 key concerns\n\n"
        "## Confidence\n"
        "- High/Medium/Low"
    ),
    agent=investment_advisor,
    tools=[search_tool],
    async_execution=False,
    context=[analyze_financial_document]
)

## Creating a risk assessment task
risk_assessment_task = Task(
    description=(
        "Assess financial risks from analysis.\n\n"
        "Context: {query}\n\n"
        "Identify:\n"
        "1. Financial risks (liquidity, solvency)\n"
        "2. Operational risks\n"
        "3. Risk level (Low/Medium/High)\n"
        "4. Mitigation strategies"
    ),
    expected_output=(
        "Risk Assessment:\n\n"
        "## Overall Risk\n"
        "- Level: Low/Medium/High\n\n"
        "## Key Risks\n"
        "- Financial risks\n"
        "- Operational risks\n\n"
        "## Mitigation\n"
        "- 3 actionable strategies"
    ),
    agent=risk_assessor,
    tools=[search_tool],
    async_execution=False,
    context=[analyze_financial_document]
)
