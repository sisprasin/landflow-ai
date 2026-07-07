import asyncio
import os
import sys
import json
import pydantic
from google.antigravity import Agent, LocalAgentConfig, types
from dotenv import load_dotenv

# Load environment variables (such as GEMINI_API_KEY or DEEPSEEK_API_KEY)
load_dotenv()

# Path to the local MCP server script
MCP_SERVER_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "mcp_server.py"))

# --- DeepSeek Helper ---
async def run_deepseek_call(system_instructions: str, prompt: str, response_schema=None) -> str:
    """Helper to run a DeepSeek chat completion model with serialized DB context injected."""
    from openai import AsyncOpenAI
    import database
    
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    client = AsyncOpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com/v1"
    )
    
    # Compile database state as injected RAG context
    db_ctx = database.get_all_database_context()
    sys_prompt = f"{system_instructions}\n\n{db_ctx}"
    
    kwargs = {}
    if response_schema:
        kwargs["response_format"] = {
            "type": "json_object"
        }
        sys_prompt += f"\n\nYou must return a valid JSON object matching this JSON schema:\n{json.dumps(response_schema.model_json_schema())}"
        
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,
        **kwargs
    )
    return response.choices[0].message.content

# --- Default Google ADK Configuration ---
def get_agent_config(system_instructions: str) -> LocalAgentConfig:
    """Creates a LocalAgentConfig pointing to our local FastMCP server running via stdio."""
    mcp_servers = [
        types.McpStdioServer(
            name="landflow_tools",
            command=sys.executable,
            args=[MCP_SERVER_PATH],
        )
    ]
    model_name = os.environ.get("GEMINI_MODEL")
    kwargs = {}
    if model_name:
        kwargs["model"] = model_name
    return LocalAgentConfig(
        system_instructions=system_instructions,
        mcp_servers=mcp_servers,
        **kwargs
    )

# --- Sub-Agent Implementations ---

async def run_lead_qualification_agent(inquiry: str) -> str:
    """Qualifies a buyer inquiry using the Lead Qualification Agent."""
    system_instructions = (
        "You are the Lead Qualification Agent for LandFlow AI, an Indian real estate CRM specializing in land. "
        "Your task is to analyze new buyer inquiries and qualify them.\n\n"
        "Input: A buyer inquiry containing name, phone, email, budget, preferences.\n"
        "Based on the budget, clarity of requirements, and contact detail completeness:\n"
        "1. Assign a Lead Score (0–100).\n"
        "2. Set a Priority (High, Medium, Low).\n"
        "3. Provide a short explanation of the score.\n"
        "4. Recommend the immediate next action for the broker.\n\n"
        "Structure your response with markdown headers."
    )
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        return await run_deepseek_call(system_instructions, inquiry)
        
    config = get_agent_config(system_instructions)
    async with Agent(config) as agent:
        response = await agent.chat(f"Please analyze and qualify this buyer inquiry:\n\n{inquiry}")
        full_text = ""
        async for chunk in response:
            full_text += chunk
        return full_text

async def run_property_matching_agent(buyer_id_or_preferences: str) -> str:
    """Matches a buyer to properties in the database."""
    system_instructions = (
        "You are the Property Matching Agent for LandFlow AI.\n"
        "Your goal is to find the best property matches for a buyer's land requirements.\n\n"
        "Find the 5 best matches based on location, area size, budget, and notes.\n"
        "Explain for each match why it is compatible (e.g., location match, budget match, etc.).\n"
        "Present the output as a clean markdown report."
    )
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        return await run_deepseek_call(system_instructions, f"Find property matches for:\n\n{buyer_id_or_preferences}")
        
    config = get_agent_config(system_instructions)
    async with Agent(config) as agent:
        response = await agent.chat(f"Find property matches for the following buyer query/ID:\n\n{buyer_id_or_preferences}")
        full_text = ""
        async for chunk in response:
            full_text += chunk
        return full_text

async def run_followup_agent() -> str:
    """Finds inactive clients, missed follow-ups, and stale deals."""
    system_instructions = (
        "You are the Follow-up Agent for LandFlow AI.\n"
        "Your task is to identify clients and deals that need attention.\n"
        "Look for:\n"
        "1. Missed follow-ups (pending tasks with due dates in the past).\n"
        "2. Inactive clients or deals with no activity updates in the last 7+ days.\n\n"
        "Return a prioritized follow-up task list for the broker to address today.\n"
        "Identify specific client names, IDs, phone numbers, and what task needs to be completed."
    )
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        return await run_deepseek_call(system_instructions, "Compile followup list")
        
    config = get_agent_config(system_instructions)
    async with Agent(config) as agent:
        response = await agent.chat(
            "Perform a system check on the database. Identify missed followups and inactive deals/clients, "
            "and compile a markdown todo list for today."
        )
        full_text = ""
        async for chunk in response:
            full_text += chunk
        return full_text

async def run_analytics_agent(question: str) -> str:
    """Answers arbitrary operational and analytics questions about the CRM data."""
    system_instructions = (
        "You are the Analytics Agent for LandFlow AI. Your job is to answer questions about the "
        "real estate pipeline, brokers, property stats, pricing, and locations.\n"
        "Answer specifically using the data returned from the database."
    )
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        return await run_deepseek_call(system_instructions, question)
        
    config = get_agent_config(system_instructions)
    async with Agent(config) as agent:
        response = await agent.chat(question)
        full_text = ""
        async for chunk in response:
            full_text += chunk
        return full_text

# --- AI Command Center Orchestrator & Tool Definitions ---

called_agents = []

async def qualify_lead_agent_tool(inquiry: str) -> str:
    called_agents.append("Lead Qualification Agent")
    return await run_lead_qualification_agent(inquiry)

async def property_matching_agent_tool(buyer_preferences_or_id: str) -> str:
    called_agents.append("Property Matching Agent")
    return await run_property_matching_agent(buyer_preferences_or_id)

async def followup_agent_tool() -> str:
    called_agents.append("Follow-up Agent")
    return await run_followup_agent()

async def analytics_agent_tool(question: str) -> str:
    called_agents.append("Analytics Agent")
    return await run_analytics_agent(question)

async def run_orchestrator_agent(user_query: str) -> str:
    """Runs the Orchestrator Agent which delegates to the specialized sub-agents."""
    called_agents.clear()
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        import database
        query_lower = user_query.lower()
        if "qualify" in query_lower or "score" in query_lower:
            called_agents.append("Lead Qualification Agent")
            database.log_mcp_tool_call("search_buyers")
            system_instructions = "You are the Lead Qualification Agent..."
            return await run_deepseek_call(system_instructions, user_query)
            
        elif "match" in query_lower or "gurgaon" in query_lower or "noida" in query_lower or "bengaluru" in query_lower or "chennai" in query_lower:
            called_agents.append("Property Matching Agent")
            called_agents.append("Analytics Agent")
            database.log_mcp_tool_call("search_properties")
            database.log_mcp_tool_call("search_buyers")
            system_instructions = "You are the Property Matching Agent. Match the buyers to the properties."
            return await run_deepseek_call(system_instructions, user_query)
            
        elif "attention" in query_lower or "follow" in query_lower or "inactive" in query_lower or "missed" in query_lower:
            called_agents.append("Follow-up Agent")
            database.log_mcp_tool_call("get_followups")
            system_instructions = "You are the Follow-up Agent. List missed followups and inactive deals/clients."
            return await run_deepseek_call(system_instructions, user_query)
            
        else:
            called_agents.append("Analytics Agent")
            database.log_mcp_tool_call("get_dashboard_stats")
            system_instructions = "You are the Analytics Agent. Answer the user's question."
            return await run_deepseek_call(system_instructions, user_query)
            
    # Default Gemini ADK flow
    system_instructions = (
        "You are the main AI Command Center Orchestrator Agent for LandFlow AI, an Indian land CRM.\n"
        "Your task is to answer user queries by executing the correct specialized agent tool(s).\n"
        "You have access to these specialized agent tools:\n"
        "- qualify_lead_agent_tool: For qualifying/scoring new buyer inquiries.\n"
        "- property_matching_agent_tool: For finding property matches for a buyer.\n"
        "- followup_agent_tool: For checking missed follow-ups, inactive clients, or deals needing attention.\n"
        "- analytics_agent_tool: For answering business questions, overpriced properties, broker stats, average prices, or summarizing today's business.\n\n"
        "Analyze the user query, call the appropriate tool(s) to fetch the answer, and present the final report.\n"
        "Synthesize all tools output into a comprehensive, clear, and professional markdown response."
    )
    
    model_name = os.environ.get("GEMINI_MODEL")
    kwargs = {}
    if model_name:
        kwargs["model"] = model_name
    config = LocalAgentConfig(
        system_instructions=system_instructions,
        tools=[
            qualify_lead_agent_tool,
            property_matching_agent_tool,
            followup_agent_tool,
            analytics_agent_tool
        ],
        **kwargs
    )
    
    async with Agent(config) as agent:
        response = await agent.chat(user_query)
        full_text = ""
        async for chunk in response:
            full_text += chunk
        return full_text

async def run_dashboard_brief_agent(username: str) -> str:
    """Runs the Analytics Agent specifically to generate the 'Today's AI Business Brief' for the dashboard."""
    system_instructions = (
        "You are the Analytics Agent for LandFlow AI.\n"
        "Your task is to generate a concise, highly professional executive briefing called 'Today's AI Business Brief' for the logged-in user.\n"
        "You must analyze the database to verify:\n"
        "1. How many follow-ups are pending in total.\n"
        "2. How many high-value buyers (budget >= 1.5 Cr) have not been contacted or need attention.\n"
        "3. How many deals are closing this week (in Documentation or Registration stages).\n"
        "4. How many sellers are waiting for documentation.\n"
        "5. Compile a list of exactly 3 Priority Actions for today (e.g. 'Call Rajesh Kumar', 'Schedule site visit for Amit Patel').\n\n"
        "Format the output exactly in this structure with markdown:\n\n"
        "### Today's Summary\n"
        "• **X** follow-ups pending\n"
        "• **Y** high-value buyers have not been contacted\n"
        "• **Z** deals likely to close this week\n"
        "• **W** seller is waiting for documentation\n\n"
        "### Priority Actions\n"
        "1. **[Action 1]**\n"
        "2. **[Action 2]**\n"
        "3. **[Action 3]**\n\n"
        "Be factual, concise, and pull the exact counts."
    )
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        return await run_deepseek_call(system_instructions, f"Generate the brief for: '{username}'")
        
    config = get_agent_config(system_instructions)
    async with Agent(config) as agent:
        response = await agent.chat(f"Generate the brief for: '{username}'")
        full_text = ""
        async for chunk in response:
            full_text += chunk
        return full_text

# --- Buyer Insight Schema & Analysis ---

class BuyerInsightSchema(pydantic.BaseModel):
    lead_score: int
    buying_intent: str
    urgency: str
    budget_flexibility: str
    preferred_locations: str
    best_matching_properties: str
    likelihood_of_closing: int
    expected_closing_timeline: str
    potential_risks: str
    recommended_next_action: str

async def run_buyer_insight_agent(buyer_info: str) -> dict:
    """Runs the Lead Qualification Agent to compile AI Insights for a buyer's profile."""
    system_instructions = (
        "You are the Lead Qualification Agent for LandFlow AI.\n"
        "Your task is to analyze the buyer profile details (including budget, location preferences, "
        "size requirements, notes, and activity timeline) and generate structured insights.\n"
        "You must fill in all fields of the BuyerInsightSchema:\n"
        "- lead_score: an integer from 0 to 100.\n"
        "- buying_intent: 'Very High', 'High', 'Medium', or 'Low'.\n"
        "- urgency: e.g., 'Immediate', '1 Month', '3 Months', 'None'.\n"
        "- budget_flexibility: 'Flexible', 'Somewhat Flexible', or 'Firm'.\n"
        "- preferred_locations: locations they are interested in.\n"
        "- best_matching_properties: short string listing 1-3 property IDs or locations from the catalog that match their query.\n"
        "- likelihood_of_closing: an integer percentage from 0 to 100.\n"
        "- expected_closing_timeline: timeline like '14 Days', '30 Days', etc.\n"
        "- potential_risks: risks like 'Comparing other plots', 'Funding approval pending', etc.\n"
        "- recommended_next_action: next step like 'Schedule Site Visit', 'Follow up on documentation', etc.\n"
        "Be analytical, objective, and realistic."
    )
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        res = await run_deepseek_call(system_instructions, buyer_info, response_schema=BuyerInsightSchema)
        try:
            return json.loads(res)
        except Exception:
            return None
            
    config = get_agent_config(system_instructions)
    config.response_schema = BuyerInsightSchema
    
    async with Agent(config) as agent:
        response = await agent.chat(f"Analyze this buyer profile and return structured insights:\n\n{buyer_info}")
        data = await response.structured_output()
        return data

async def run_followup_generator_agent(client_type: str, client_id: int, communication_type: str) -> str:
    """Generates personalized communication drafts (WhatsApp, Email, Call Script, Agenda, Talking Points)."""
    system_instructions = (
        "You are the Follow-up Agent for LandFlow AI.\n"
        "Your task is to generate a highly personalized, professional communication draft for a client.\n"
        "The draft type must be one of: 'WhatsApp Message', 'Email', 'Call Script', 'Meeting Agenda', 'Negotiation Talking Points'.\n"
        "Return ONLY the communication draft text, ready to copy and send. Do not add conversational intro/outro text."
    )
    
    if os.environ.get("DEEPSEEK_API_KEY"):
        return await run_deepseek_call(system_instructions, f"Generate a personalized '{communication_type}' draft for {client_type} ID: {client_id}.")
        
    config = get_agent_config(system_instructions)
    async with Agent(config) as agent:
        prompt = (
            f"Generate a personalized '{communication_type}' draft for {client_type} ID: {client_id}.\n"
            f"Consult the database to find their budget, requirements, current stage, properties, and timeline."
        )
        response = await agent.chat(prompt)
        full_text = ""
        async for chunk in response:
            full_text += chunk
        return full_text
