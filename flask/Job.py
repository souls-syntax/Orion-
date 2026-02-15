import sys
import json
import google.generativeai as genai

genai.configure(api_key="Enter your Google API key here")

model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def get_job_assistance(current_job, current_salary, experience, expected_salary, expected_company, expected_job_role):
    prompt = f"""
    Act as an AI Job Assistant Bot.

    User Information:
    - Current Job Role: {current_job}
    - Current Salary: {current_salary} per annum
    - Experience: {experience} years
    - Expected Salary: {expected_salary} per annum
    - Expected Company: {expected_company}
    - Expected Job Role: {expected_job_role}

    Please provide an answer by comparing the current job with the expected job parameters in the following format:

    ```json
    {{
        "Coding_Question":
            [
                {{
                    "Question": "<MUST BE a Relevant Coding Question Text directly related to the skills required for the Expected Job Role: {expected_job_role}>",
                    "difficulty": "<Question Difficulty (e.g., Easy, Medium, Hard)>",
                    "DSA": "<Which specific part of Data Structures and Algorithms is primarily used in this question (e.g., Arrays, Linked Lists, Trees, Sorting, Searching, Dynamic Programming)>",
                    "Link": "<MUST BE a Verified, Currently Working Link to a reputable platform (e.g., LeetCode, GeeksforGeeks) where this question or a very similar one can be found.>",
                    "Question_description": "<A concise and accurate description of the coding problem.>"
                }} ...
            ],
        "Interviews":
            [
                {{
                    "Interview_name": "<Relevant Interview Type or Name (e.g., Technical Screening, HR Interview, System Design Interview)>",
                    "interview_description": "<An accurate description of what this type of interview typically entails, focusing on aspects relevant to the Expected Job Role: {expected_job_role} and potentially the interview process at {expected_company}.>"
                }} ...
            ],
        "Placement_Rounds":
            [
                {{
                    "round_name": "<Round Name (e.g., Online Assessment, Technical Interview Round 1, Group Discussion)>",
                    "Round_Description": "<An accurate description of what this round typically involves in the context of hiring for the Expected Job Role: {expected_job_role} and potentially at {expected_company}.>",
                    "Round_Duration": "<Typical duration of this round (e.g., '60 minutes', '2 days').>"
                }} ...
            ],
        "Course_Content":
            [
                {{
                     "content_name": "<Content Name (e.g., 'Introduction to Data Structures', 'Advanced React Concepts', 'Behavioral Interview Strategies')>",
                    "content_description": "<An accurate and concise description of what this course content covers, emphasizing its relevance to the Expected Job Role: {expected_job_role}.>",
                    "course_link": "<MUST BE a Verified, Currently Working Link to a reputable online learning platform (e.g., Coursera, Udemy, edX, Udacity) offering this or a very similar course.>"
                }} ...
            ],
        "Youtube_Videos":
            [
                {{
                    "youtube_video_name": "<Concise Video Title>",
                    "youtube_video_link": "<Provide ONE VERIFIED, CURRENTLY WORKING YouTube link to a video that DIRECTLY helps with a skill for {expected_job_role} or interview preparation for a similar role. ONLY include if the link is functional as of today's date. If no such link exists, leave this array empty.>"
                }} ...
            ],
        "Important_Consideration":
            [
                "<MUST BE a concise and accurate point that is genuinely important for someone transitioning from {current_job} to {expected_job_role} at {expected_company} (if specified).>" ...
            ],
        "Summary": "<MUST BE an accurate and concise summary that highlights the key differences and similarities between the current job and the expected job parameters, and provides a realistic overview of the transition.>"
    }}
    ```
"""


    response = model.generate_content(prompt)
    raw_output = response.text.strip()

    # Attempt to extract valid JSON from within ```json markdown
    if "```json" in raw_output:
        try:
            json_start = raw_output.find("```json") + 7
            json_end = raw_output.rfind("```")
            json_str = raw_output[json_start:json_end].strip()
            return json.loads(json_str)
        except json.JSONDecodeError:
            return {"error": "Failed to parse JSON from Gemini output.", "raw_output": raw_output}

    return {"error": "Gemini response did not contain JSON format.", "raw_output": raw_output}
