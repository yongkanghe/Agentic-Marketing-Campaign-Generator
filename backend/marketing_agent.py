"""Marketing Campaign Content Generator using ADK SequentialAgent.

This module exposes ``root_agent`` which can be executed with
``google-adk`` runners. The agent orchestrates a workflow to
summarize business details, generate campaign ideas and produce
short social media posts.
"""

from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.agents.llm_agent import LlmAgent

# Gemini model to use. This can be customised.
GEMINI_MODEL = "gemini-2.0-pro"

# --- Sub Agents ---
summary_agent = LlmAgent(
    name="SummaryAgent",
    model=GEMINI_MODEL,
    instruction="""You are a marketing assistant.
Summarize the business description and objective provided by the user
into a short paragraph. Use {business_description} and {objective}
as your context.""",
    description="Summarizes the user's business and campaign objective.",
    output_key="summary",
)

idea_agent = LlmAgent(
    name="IdeaAgent",
    model=GEMINI_MODEL,
    instruction="""Using the campaign summary: {summary},
create three concise marketing campaign ideas. Return each idea on a
new line as 'Idea X: ...'.""",
    description="Generates marketing campaign ideas.",
    output_key="ideas",
)

social_agent = LlmAgent(
    name="SocialPostAgent",
    model=GEMINI_MODEL,
    instruction="""For each marketing idea in {ideas},
write a short engaging social media post no longer than 280 characters.
Return each post on a new line prefixed with the idea number.""",
    description="Produces short social media posts for the ideas.",
    output_key="posts",
)

# --- Root Sequential Agent ---
root_agent = SequentialAgent(
    name="MarketingCampaignAgent",
    sub_agents=[summary_agent, idea_agent, social_agent],
    description="Generates marketing campaign content in sequence.",
)
