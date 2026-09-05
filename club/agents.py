import os
from typing import TypedDict, Annotated, Literal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# Define State Structure
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    age_group: str        # e.g., '5-8', '9-12', '13-17', '18+'
    tutor_type: str       # 'coding' or 'finance'

# Initialize LLM
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    api_key=os.getenv("OPENAI_API_KEY")
)

# ----------------------------------------------------
# 1. CODING TUTOR NODE
# ----------------------------------------------------
def coding_tutor_node(state: AgentState) -> dict:
    age = state.get("age_group", "9-12")
    
    system_prompts = {
        "5-8": (
            "You are SmartKids Coding Buddy! Explain programming concepts using fun stories, "
            "LEGO analogies, blocks, and simple logic puzzles. Keep answers under 3 sentences."
        ),
        "9-12": (
            "You are SmartKids Coding Mentor! Teach Python and web concepts with gamified examples, "
            "simple logic snippets, and clear step-by-step guidance."
        ),
        "13-17": (
            "You are SmartKids Tech Guide! Teach real-world code (Python, Django, HTML/CSS, JS), "
            "best practices, debugging tips, and practical project guidance."
        ),
        "18+": (
            "You are SmartKids Senior Tech Advisor! Provide precise technical guidance on software "
            "architecture, Django, web engineering, and algorithms."
        )
    }
    
    prompt = system_prompts.get(age, system_prompts["9-12"])
    messages = [SystemMessage(content=prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# ----------------------------------------------------
# 2. FINANCE TUTOR NODE
# ----------------------------------------------------
def finance_tutor_node(state: AgentState) -> dict:
    age = state.get("age_group", "9-12")
    
    system_prompts = {
        "5-8": (
            "You are SmartKids Money Penny! Explain saving, coins, and piggy banks using "
            "fun toy-store examples and simple stories."
        ),
        "9-12": (
            "You are SmartKids Finance Coach! Teach budgeting, earning, saving vs. spending, "
            "and basic entrepreneurship in an engaging way."
        ),
        "13-17": (
            "You are SmartKids Financial Advisor! Cover personal budgeting, interest rates, "
            "investing basics, digital currency safety, and financial independence."
        ),
        "18+": (
            "You are SmartKids Financial Strategist! Provide comprehensive insights on financial "
            "planning, asset allocation, budgeting models, and economic concepts."
        )
    }
    
    prompt = system_prompts.get(age, system_prompts["9-12"])
    messages = [SystemMessage(content=prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}

# ----------------------------------------------------
# 3. ROUTER / ORCHESTRATOR
# ----------------------------------------------------
def route_agent(state: AgentState) -> Literal["coding_tutor", "finance_tutor"]:
    tutor = state.get("tutor_type", "coding").lower()
    if tutor == "finance":
        return "finance_tutor"
    return "coding_tutor"

# Build LangGraph StateMachine
workflow = StateGraph(AgentState)

workflow.add_node("coding_tutor", coding_tutor_node)
workflow.add_node("finance_tutor", finance_tutor_node)

workflow.add_conditional_edges(START, route_agent)
workflow.add_edge("coding_tutor", END)
workflow.add_edge("finance_tutor", END)

# Compile graph
tutor_graph = workflow.compile()


def run_tutor_agent(message: str, age_group: str, tutor_type: str) -> str:
    """Helper function to execute graph execution synchronously."""
    initial_state = {
        "messages": [HumanMessage(content=message)],
        "age_group": age_group,
        "tutor_type": tutor_type
    }
    output = tutor_graph.invoke(initial_state)
    return output["messages"][-1].content