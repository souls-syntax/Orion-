import os
import re
import json
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from google import genai

# Configure the Tesseract executable path if it's not in your PATH
tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# Configure Google Gemini
GOOGLE_API_KEY = "Enter your Google API key here"
client = genai.Client(api_key=GOOGLE_API_KEY)

def convert_pdf_to_png(pdf_path: str) -> list:
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_dir = f"{base_name}_pages"
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(pdf_path)
    png_paths = []
    for i, image in enumerate(images, start=1):
        png_path = os.path.join(output_dir, f"{base_name}_page_{i}.png")
        image.save(png_path, "PNG")
        png_paths.append(png_path)
    return png_paths

def extract_text_from_image(image_path: str) -> str:
    img = Image.open(image_path)
    return pytesseract.image_to_string(img)

def fetch_job_descriptions(company_name: str) -> str:
    prompt = f"""
    Provide detailed job descriptions (approximately 100-150 words for the Job Summary and 5-8 bullet points each for Responsibilities and Qualifications and Skills) for at least 5 distinct positions available at {company_name}.

    If the provided company name '{company_name}' is incorrect or no exact matches are found, identify and use the closest well-known company name in the same industry. Clearly state the company name you are using in the response.

    For each of the at least 5 positions, include the following sections with clear headings:
    1. Job Title: The official name of the position.
    2. Job Summary: A concise overview of the role's primary purpose and key responsibilities.
    3. Responsibilities: A bulleted list of the main tasks and duties.
    4. Qualifications and Skills: A bulleted list of required education, experience, technical proficiencies, and soft skills.
    """
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text

def match_roles(resume_text: str, job_descriptions: str, user_job_description: str) -> str:
    prompt = f"""
    You are an ATS (Applicant Tracking System) and career advisor.

    Analyze the following resume in the context of the given job descriptions.

    **Crucially, filter the generated list of 'SuitableRoles' to include ONLY those positions from the 'Job Descriptions' that demonstrate a strong alignment (aim for at least 60-70% keyword and core skill overlap) with the following expected job description provided by the user:**
    {user_job_description}

    Provide:
    1. An ATS Score (0 to 100) for the MOST suitable role(s) based on a weighted matching of:
        - Keywords (specific technical terms, job titles) present in both the resume and the job description (weight: 60%).
        - Core skills (essential abilities explicitly mentioned) present in both (weight: 40%). Briefly explain the rationale behind the score, highlighting key strengths and areas of mismatch.
    2. Suggestions for improving the resume to better match relevant roles, divided into the following sections:
        - Achievements: Offer 2-3 specific, actionable suggestions on how to better quantify accomplishments and highlight their relevance to target roles.
        - Certifications: Suggest 1-2 relevant industry-recognized certifications that could strengthen the candidate's profile for the expected job description.
        - Overall: Provide 2-3 general tips on how to improve the resume's clarity, conciseness, and focus on the desired career path.

    Return the result in JSON format using the following structure:
    ```json
    {{
        "ATS": {{
            "Score": <integer>,
            "Explanation": "<brief explanation of the ATS score>",
            "Suggestions": {{
                "Achievements": <list of 2-3 actionable suggestions>,
                "Certifications": <list of 1-2 relevant certifications to consider>,
                "Overall": <list of 2-3 general improvement tips>
            }}
        }},
        "SuitableRoles": [{{
            "Role_name": <string>,
            "Reasoning": "<A concise explanation of why this specific role is considered suitable, explicitly referencing the skills and experience from the resume that align with the job description and the user's expected job description.>"
        }}, {{
            "Role_name": <string>,
            "Reasoning": "<A concise explanation of why this specific role is considered suitable, explicitly referencing the skills and experience from the resume that align with the job description and the user's expected job description.>"
        }}
        ...]
    }}
    ```

    Replace <...> with the actual data. Ensure the 'Suggestions' lists contain actionable and specific advice. If no suitable roles are found, the 'SuitableRoles' array should be empty.

    Resume:
    {resume_text}

    Job Descriptions:
    {job_descriptions}

    Provide a response in the exact JSON format described above.
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )
    return response.text
