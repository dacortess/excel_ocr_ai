from flask import Flask, request, jsonify, send_file
import google.generativeai as genai
from dotenv import load_dotenv
import os
import PIL.Image
import json
import pandas as pd
import re

app = Flask(__name__)

# Load environment variables
load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))

# Initialize model
model = genai.GenerativeModel(model_name="gemini-2.0-flash")

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    image_file = request.files['image']
    image_path = "uploaded_image.jpg"
    image_file.save(image_path)
    image = PIL.Image.open(image_path)

    # Define prompt
    prompt = """Extract the data from the table in the image and return it as a JSON object.  
    The JSON should represent the table structure, where keys are column headers and values 
    are lists of corresponding cell values e.g. {"Column 1": ["value 1.1", "value 1.2"], "Column 2": ["value 2.1", "value 2.2"]}. 
    If there are no explicit headers, create generic ones like Column 1, Column 2, etc.
    """

    # Get response from Gemini API
    response = model.generate_content([image, prompt])
    response_text = response.text.strip()
    match = re.search(r"\{.*\}", response_text, re.DOTALL)

    if match:
        json_text = match.group(0)
        json_data = json.loads(json_text)
    else:
        return jsonify({"error": "No valid table data found"}), 500

    # Convert JSON to DataFrame
    df = pd.DataFrame(json_data)
    excel_path = "table_data.xlsx"
    df.to_excel(excel_path, index=False)

    return send_file(excel_path, as_attachment=True, download_name='table_data.xlsx')

if __name__ == '__main__':
    app.run(debug=True)