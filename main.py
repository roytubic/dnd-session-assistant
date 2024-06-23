import os
from dotenv import load_dotenv
from groq import Groq
from transformers import AutoTokenizer

load_dotenv()

os.environ["TOKENIZERS_PARALLELISM"] = "false"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

model_id = "meta-llama/Meta-Llama-3-70B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id, token=os.environ.get("HUGGINGFACE_TOKEN"))

def load_template(file_path):
    with open(file_path, 'r') as file:
        template = file.read()
    return template

def generate_partial_session_plan(inputs, story_points):
    session_plan = f"""
PCs:
{inputs['PCs']}

NPCs:
{inputs['NPCs']}

Session #:
{inputs['session_number']}

Session Opening Cinematic:
{inputs['session_opening']}

"""
    for i in range(1, story_points + 1):
        session_plan += f"""
Story point #: {i} (Expected time spent on scene)
Date and time: {inputs['story_points'][i-1]['in_game_date']}
GM NOTE: {inputs['story_points'][i-1]['gm_note']}

SCENE CINEMATIC:
{inputs['story_points'][i-1]['scene_cinematic']}

LOCATION: 
Use the senses!!

WHO’S THERE:
{inputs['story_points'][i-1]['whos_there']}

BIG CLUE TO REVEAL - NO ROLLS REQUIRED:
{inputs['story_points'][i-1]['big_clue']}

"""
    return session_plan

def collect_inputs():
    inputs = {}
    inputs['PCs'] = input("Enter Player Character names and brief description: ")
    inputs['NPCs'] = input("Enter Names of the NPC’s currently traveling with the party: ")
    inputs['session_number'] = input("Enter Session Number: ")
    inputs['session_opening'] = input("Enter Session Opening Cinematic: ")
    
    story_points = int(input("Enter the number of story points: "))
    inputs['story_points'] = []

    for i in range(1, story_points + 1):
        story_point = {}
        story_point['in_game_date'] = input(f"Enter In-game Date for story point {i}: ")
        story_point['gm_note'] = input(f"Enter GM Note for story point {i}: ")
        story_point['scene_cinematic'] = input(f"Enter Scene Cinematic for story point {i}: ")
        story_point['whos_there'] = input(f"Enter NPCs/Monsters in the scene for story point {i}: ")
        story_point['big_clue'] = input(f"Enter Big Clue to reveal for story point {i}: ")
        inputs['story_points'].append(story_point)

    return inputs, story_points

def expand_session_plan(partial_plan):
    expansion_prompt = f"""
Here is a partial session plan for a Dungeons & Dragons session. Please expand on this plan, adding details, filling in gaps, and enhancing it to create a complete session plan. Make sure to integrate and build upon the provided inputs cohesively. Fill in the following sections with appropriate content: dialogue, skill checks, environmental hazards, charm/persuade opportunities, perception/notice opportunities.

{partial_plan}
"""

    expansion_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": expansion_prompt},
        ],
        model="llama3-70b-8192",
        stream=True,
        temperature=0.9,
    )

    expanded_plan = ""
    for chunk in expansion_completion:
        content = chunk.choices[0].delta.content
        if content:
            expanded_plan += content

    return expanded_plan

template_path = 'session-template.txt'
template = load_template(template_path)

while True:

    user_input = input("You: ")

    if user_input.lower() in ['exit', 'quit']:
        print("Goodbye!")
        break
    
    if user_input.lower() == 'start session plan':
        inputs, story_points = collect_inputs()
        partial_session_plan = generate_partial_session_plan(inputs, story_points)
        print("Generating session plan...")
        expanded_session_plan = expand_session_plan(partial_session_plan)
        print("Session Plan Complete:")
        print(expanded_session_plan)
        continue
