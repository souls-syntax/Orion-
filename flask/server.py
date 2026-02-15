from flask import Flask, jsonify, request
from flask_cors import CORS
from ATS import *
from CodeBot import *
from Job import *

app = Flask(__name__)
CORS(app)

@app.route('/')
def home():
    return jsonify(message="Hello from Flask!")

@app.route('/ats', methods=['POST'])
def ats_evaluation():
    data = request.get_json()
    company_name = data.get('company_name')
    pdf_path = data.get('pdf_path')
    user_job_description = data.get('user_job_description')

    if not (company_name and pdf_path and user_job_description):
        return jsonify({"error": "Missing required fields"}), 400

    if pdf_path.lower().endswith('.pdf'):
        png_files = convert_pdf_to_png(pdf_path)
    else:
        png_files = [pdf_path]

    all_texts = []
    for png in png_files:
        text = extract_text_from_image(png)
        all_texts.append(text)
    resume_text = "\n".join(all_texts)

    job_descriptions = fetch_job_descriptions(company_name)
    role_matches = match_roles(resume_text, job_descriptions, user_job_description)

    try:
        json_pattern = r'```json\n(.*?)\n```'
        match = re.search(json_pattern, role_matches, re.DOTALL)
        if match:
            json_data = match.group(1)
            parsed_json = json.loads(json_data)
            return jsonify(parsed_json)
        else:
            return jsonify({"error": "No JSON format found in Gemini response.", "raw": role_matches}), 500
    except json.JSONDecodeError as e:
        return jsonify({"error": "Failed to parse JSON", "details": str(e), "raw": role_matches}), 500

@app.route("/codebot", methods=["POST"])
def codebot_route():
    data = request.get_json()
    if not data or "code" not in data:
        return jsonify({"error": "Missing 'code' in request body."}), 400

    code = data["code"]
    language = data.get("language", "auto")

    result = codebot_api_handler(code, language)
    return jsonify(result)

@app.route("/job-assist", methods=["POST"])
def job_assist():
    try:
        data = request.get_json()
        required_fields = [
            "current_job", "current_salary", "experience",
            "expected_salary", "expected_company", "expected_job_role"
        ]
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields."}), 400

        result = get_job_assistance(
            data["current_job"],
            data["current_salary"],
            data["experience"],
            data["expected_salary"],
            data["expected_company"],
            data["expected_job_role"]
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)