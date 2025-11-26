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
import google.auth
from google.adk.agents import Agent

# --- Boilerplate Setup ---
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")


# --- Step 1: Define all tools as plain Python functions ---
# The docstrings (the text in """...""") are critical because the model uses them
# to decide which tool to use.

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
    # In a real application, this would interact with a database (e.g., Firestore).
    print(f"Accessing Memory: User='{user_id}', Mode='{mode}', Data='{data}'")
    if mode == "read_summary":
        return "User previously struggled with irregular past tense verbs."
    return "Memory access successful."

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
    print(f"Creating learning plan for level '{current_level}'...")
    return f"Weekly Plan Created: Focus on '{goals}', building on past performance."

def generate_assessment(
    topic: str,
    num_questions: int = 5,
    focus_on_past_mistakes: bool = True
) -> str:
    """
    Use this to create a quiz on a specific topic, often informed by the user's
    past mistakes from long-term memory. Returns a set of questions and answers.
    """
    print(f"Generating a {num_questions}-question quiz on '{topic}'...")
    return f"Quiz on '{topic}' is ready."

def setup_scenario(scenario_name: str, difficulty: str = "intermediate") -> str:
    """
    Use this to get the details for a role-playing scenario. Returns the setting,
    your role, and an opening line to start the conversation.
    """
    print(f"Setting up '{scenario_name}' scenario at {difficulty} difficulty...")
    return f"Scenario ready: You are at a restaurant. Your opening line is 'Hello, a table for one, please.'"


# --- Step 2: Define the Main Orchestrator Agent ---

PROFESSOR_TUTOR_PROMPT = """
You are Professor Tutor, the lead agent and orchestrator of a language learning crew. Your personality is friendly, patient, and expert. Your primary role is to manage the user's learning journey by understanding their needs and delegating tasks to the appropriate tools.

**Your Capabilities (Tools):**
- Plan Creation: You can create structured, long-term learning schedules.
- Role-Playing: You can run immersive, real-world scenarios.
- Assessment: You can design and administer quizzes to identify and reinforce weak points.
- Memory: You can save and retrieve user progress.

**Your Thought Process:**
Before responding to the user, you MUST engage in a silent, internal monologue using <thinking> tags. This is your core operational loop.

1.  **Analyze Request:** What is the user's explicit and implicit goal?
2.  **Recall from Memory:** Use the `access_long_term_memory` tool to retrieve relevant user history, past struggles, and preferences.
3.  **Choose Tool or Respond:** Decide if this is a simple conversational task you handle yourself, or if it requires a specialist tool.
4.  **Formulate Response:** Based on the above, construct your response to the user.

**Rules of Engagement:**
1.  **Orchestration:** Your main job is to choose the right tool. When a task is complex, inform the user which tool you are using.
2.  **Memory is Key:** You MUST use the `access_long_term_memory` tool to personalize every interaction.
3.  **Continuity:** After a tool completes a task, you will resume the conversation, summarize the results, and use the `access_long_term_memory` tool to save the outcome.
"""

# We create a single agent and pass it ALL available tools
root_agent = Agent(
    name="Professor_Tutor",
    model="gemini-2.5-pro",  # Using a powerful model for orchestration is recommended
    instruction=PROFESSOR_TUTOR_PROMPT,
    tools=[
        access_long_term_memory,
        create_learning_plan,
        generate_assessment,
        setup_scenario
    ]
)

# --- Example Usage ---
if __name__ == "__main__":
    print("Starting conversation with Professor Tutor...")

    # Example 1: A task that requires the assessment tool
    response = root_agent.chat("Can you test me on my past tense verbs?")
    print(f"\nProfessor Tutor's Response:\n{response}")

    # Example 2: A task that requires the role-playing tool
    response = root_agent.chat("I'd like to practice ordering a coffee.")
    print(f"\nProfessor Tutor's Response:\n{response}")
