# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from typing import List

import google.auth
from google.adk.agents import Agent
from google.adk.tools import tool

# --- Boilerplate Setup ---
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# --- Step 1: Define the Tools for the Professor Tutor Crew ---
# The docstrings (the text in """...""") are critical. They are the descriptions
# the agent uses to decide which tool to call.

@tool
def access_long_term_memory(
    user_id: str,
    mode: str,
    data: str = ""
) -> str:
    """
    Use this tool to read from or write to the user's permanent memory file.
    Essential for personalization and tracking progress.
    'mode' can be 'write', 'read_summary', or 'query_mistakes'.
    """
    # Application interact with a database (e.g., Firestore).
    print(f"🧠 Accessing Memory: User='{user_id}', Mode='{mode}', Data='{data}'")
    if mode == "read_summary":
        return "User previously struggled with irregular past tense verbs."
    return "Memory access successful."

@tool
def create_learning_plan(
    current_level: str,
    goals: str,
    time_per_week: int,
    past_performance_summary: str
) -> str:
    """
    Use this to create a structured, weekly learning plan based on user goals
    and past performance. Returns a day-by-day schedule of activities.
    """
    print(f"📅 Creating learning plan for level '{current_level}'...")
    return f"Weekly Plan Created: Focus on '{goals}', building on past performance."

@tool
def generate_assessment(
    topic: str,
    num_questions: int = 5,
    focus_on_past_mistakes: bool = True
) -> str:
    """
    Use this to create a quiz on a specific topic, often informed by the user's
    past mistakes from long-term memory. Returns a set of questions and answers.
    """
    print(f"📝 Generating a {num_questions}-question quiz on '{topic}'...")
    return f"Quiz on '{topic}' is ready."

@tool
def setup_scenario(scenario_name: str, difficulty: str = "intermediate") -> str:
    """
    Use this to get the details for a role-playing scenario. Returns the setting,
    your role, and an opening line to start the conversation.
    """
    print(f"🎭 Setting up '{scenario_name}' scenario at {difficulty} difficulty...")
    return f"Scenario ready: You are at a restaurant. Your opening line is 'Hello, a table for one, please.'"


# --- Step 2: Define the Specialist Sub-Agents ---

planner_agent = Agent(
    name="Planner_Agent",
    model="gemini-1.5-pro-latest",
    instruction="Your sole purpose is to create effective learning plans using your tools.",
    tools=[create_learning_plan, access_long_term_memory]
)

role_player_agent = Agent(
    name="Role_Player_Agent",
    model="gemini-1.5-pro-latest",
    instruction="Your sole purpose is to engage the user in realistic role-playing scenarios using your tools.",
    tools=[setup_scenario]
)

assessor_agent = Agent(
    name="Assessor_Agent",
    model="gemini-1.5-pro-latest",
    instruction="Your sole purpose is to create and run effective assessments using your tools, leveraging the user's long-term memory to target weak areas.",
    tools=[generate_assessment, access_long_term_memory]
)


# --- Step 3: Define the Main Orchestrator Agent: Professor Tutor ---

PROFESSOR_TUTOR_PROMPT = """
You are Professor Tutor, the lead agent and orchestrator of a language learning crew. Your personality is friendly, patient, and expert. Your primary role is to manage the user's learning journey by understanding their needs and delegating tasks to your specialist agents.

**Your Specialist Team:**
- Planner_Agent: Creates structured, long-term learning schedules.
- Role_Player_Agent: An expert actor who runs immersive, real-world scenarios.
- Assessor_Agent: Designs and administers quizzes to identify and reinforce weak points.

**Your Chain-of-Thought Process:**
Before responding to the user, you MUST engage in a silent, internal monologue using <thinking> tags. This is your core operational loop.

1.  **Analyze Request:** What is the user's explicit and implicit goal?
2.  **Recall from Memory:** Access the Long-Term Memory tool to retrieve relevant user history, past struggles, and preferences.
3.  **Delegate or Handle:** Decide if this is a simple conversational task you handle yourself, or if it requires a specialist.
4.  **Formulate Response:** Based on the above, construct your response to the user.

**Rules of Engagement:**
1.  **Orchestration:** Your main job is to delegate. When a task is complex, announce which specialist is taking over.
2.  **Memory is Key:** You MUST use the `access_long_term_memory` tool to personalize every interaction.
3.  **Continuity:** After a specialist agent completes a task, you will resume the conversation, summarize the results, and use the `access_long_term_memory` tool to save the outcome.
"""

root_agent = Agent(
    name="Professor_Tutor",
    model="gemini-1.5-pro-latest",  # Using a powerful model for orchestration is recommended
    instruction=PROFESSOR_TUTOR_PROMPT,
    tools=[access_long_term_memory],  # The orchestrator's main tool is memory
    sub_agents=[  # Assign the specialist agents here
        planner_agent,
        role_player_agent,
        assessor_agent
    ]
)

# --- Example Usage ---
if __name__ == "__main__":
    print("Starting conversation with Professor Tutor...")
    
    # Example 1: A task that requires delegation to the Assessor_Agent
    response = root_agent.chat("Can you test me on my past tense verbs?")
    print(f"\nProfessor Tutor's Response:\n{response}")

    # Example 2: A task for the Role_Player_Agent
    response = root_agent.chat("I'd like to practice ordering a coffee.")
    print(f"\nProfessor Tutor's Response:\n{response}")
