import google.generativeai as genai
from dotenv import load_dotenv
import os
import PIL.Image
import json
import pandas as pd
import re

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Load image
image_path = os.path.join(os.getcwd(), 'img', 'image.jpg')
image = PIL.Image.open(image_path)

# Initialize model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

# Define prompt
prompt = """Extract the data from the table in the image and return it as a JSON object.  
The JSON should represent the table structure, where keys are column headers and values 
are lists of corresponding cell values e.g. {"Column 1": ["value 1.1", "value 1.2"], "Column 2": ["value 2.1", "value 2.2"]}. 
If there are no explicit headers, create generic ones like Column 1, Column 2, etc.
"""

# Get response from Gemini API
response = model.generate_content([image, prompt])

# Debug: Print response to check if it's valid JSON
#print(f"Response Text:\n{response.text}\n")

# Extract JSON part if extra text is present
response_text = response.text.strip()
match = re.search(r"\{.*\}", response_text, re.DOTALL)

if match:
    json_text = match.group(0)  # Extract JSON
    json_data = json.loads(json_text)
else:
    raise ValueError("No valid JSON found in response")

# Save JSON to a file
json_file_path = os.path.join(os.getcwd(), 'json', 'table_data.json')
with open(json_file_path, 'w', encoding='utf-8') as json_file:
    json.dump(json_data, json_file, indent=4)

# Convert JSON to Pandas DataFrame
df = pd.DataFrame(json_data)

excel_path = os.path.join(os.getcwd(), 'xlsx', 'table_data.xlsx')

# Save DataFrame to Excel
df.to_excel(excel_path, index=False)

print(f"JSON saved at: {json_file_path}")
print("Excel file saved as 'table_data.xlsx'.")
