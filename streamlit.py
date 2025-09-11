# app.py
import streamlit as st
import os
import json
import re
import boto3
from botocore.exceptions import NoCredentialsError
import fitz  # PyMuPDF

# -------------------- AWS SETTINGS --------------------
AWS_ACCESS_KEY_ID = "AKIAS66UDIHPHRDJ2XMP"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "ap-south-1"
S3_BUCKET_NAME = "studysmartdocuments"

# -------------------- LOCAL TEMP FOLDERS --------------------
TEMP_IMAGE_FOLDER = "temp_images"
TEMP_PDF_FILE = "temp_pdf.pdf"
OUTPUT_FOLDER = "output_maths"
OUTPUT_JSON = os.path.join(OUTPUT_FOLDER, "maths_questions.json")

os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# -------------------- S3 CLIENT --------------------
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# -------------------- FUNCTIONS --------------------
def upload_images_to_s3(s3_folder):
    uploaded_links = {}
    for filename in os.listdir(TEMP_IMAGE_FOLDER):
        if filename.lower().endswith(".jpeg"):
            local_path = os.path.join(TEMP_IMAGE_FOLDER, filename)
            s3_key = f"{s3_folder}/{filename}"

            try:
                s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
                file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
                q_match = re.search(r'(Q\d+)', filename, re.IGNORECASE)
                if q_match:
                    q_num = q_match.group(1).upper()
                    uploaded_links[q_num] = file_url
            except FileNotFoundError:
                st.error(f"File not found: {local_path}")
            except NoCredentialsError:
                st.error("AWS credentials not available")
    return uploaded_links

def process_maths_pdf(pdf_path, s3_links):
    def get_question_type(q_num):
        if 1 <= q_num <= 150: return "MCQ"
        if 151 <= q_num <= 185: return "ShortAnswer"
        if 186 <= q_num <= 200: return "LongAnswer"
        return "Unknown"

    def clean_text(text: str) -> str:
        return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()

    def parse_questions_to_json_structure(lines):
        all_questions_data = []
        full_text = "\n".join(lines)
        question_blocks = re.split(r'\n(?=\s*\d{1,3}\s*\.)', full_text)

        for block in question_blocks:
            block = block.strip()
            if not block:
                continue
            q_num_match = re.match(r'^\s*(\d{1,3})\s*\.\s*(.*)', block, re.DOTALL)
            if not q_num_match:
                continue

            q_num = int(q_num_match.group(1))
            question_type = get_question_type(q_num)
            content_text = q_num_match.group(2).strip()

            question_data = {
                "questionNUM": f"Q{q_num}",
                "questionType": question_type,
                "image": s3_links.get(f"Q{q_num}", None)
            }

            # MCQ
            if question_type == "MCQ":
                parts = re.split(r'\nAnswer:\s*', content_text, flags=re.IGNORECASE, maxsplit=1)
                if len(parts) < 2:
                    continue
                question_and_options_part, answer_part = parts
                question_text_lines, options = [], []
                for line in question_and_options_part.split('\n'):
                    stripped_line = line.strip()
                    if re.match(r'^[A-D]\)\s*', stripped_line):
                        options.append(re.sub(r'^[A-D]\)\s*', '', stripped_line).strip())
                    else:
                        question_text_lines.append(line)
                question_data["question"] = clean_text("\n".join(question_text_lines))
                question_data["options"] = [clean_text(opt) for opt in options]
                question_data["mark"] = 1

                answer_letter_match = re.search(r'^\s*([A-D])\b', answer_part.strip(), re.IGNORECASE)
                correct_answer_text = ""
                correct_option_index = None
                if answer_letter_match:
                    answer_letter = answer_letter_match.group(1).upper()
                    idx = ord(answer_letter) - ord('A')
                    if 0 <= idx < len(options):
                        correct_answer_text = options[idx]
                        correct_option_index = idx + 1
                else:
                    cleaned_answer = re.sub(r'^[A-D]\)\s*', '', answer_part.strip()).strip()
                    correct_answer_text = cleaned_answer
                    if cleaned_answer in options:
                        correct_option_index = options.index(cleaned_answer)
                question_data["correctAnswer"] = clean_text(correct_answer_text)
                question_data["correctOptionIndex"] = correct_option_index

            # Short/Long Answer
            elif question_type in ["ShortAnswer", "LongAnswer"]:
                keywords_split = re.split(r'\nKeywords:\s*', content_text, flags=re.IGNORECASE, maxsplit=1)
                main_content = keywords_split[0]
                keywords_text = keywords_split[1] if len(keywords_split) > 1 else ""
                answer_split = re.split(r'\nAnswer:\s*', main_content, flags=re.IGNORECASE, maxsplit=1)
                if len(answer_split) < 2:
                    continue
                before_answer_part, answer_part = answer_split
                solution_split = re.split(r'\nSolution:\s*', before_answer_part, flags=re.IGNORECASE, maxsplit=1)
                question_data["question"] = clean_text(solution_split[0] if len(solution_split) > 1 else before_answer_part)
                question_data["solution"] = clean_text(solution_split[1]) if len(solution_split) > 1 else ""
                question_data["correctAnswer"] = clean_text(answer_part)
                question_data["answerKeyword"] = [clean_text(k) for k in keywords_text.split(',') if k.strip()]
                question_data["mark"] = 2 if question_type == "ShortAnswer" else 5

            all_questions_data.append(question_data)
        return all_questions_data

    pdf_document = fitz.open(pdf_path)
    extracted_text = "".join(page.get_text() for page in pdf_document)
    pdf_document.close()

    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
    all_questions = parse_questions_to_json_structure(lines)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as json_file:
        json.dump(all_questions, json_file, indent=4, ensure_ascii=False)

    return all_questions

# -------------------- STREAMLIT UI --------------------
st.title("📘 Maths Question Processor with S3 Upload")

# 1️⃣ S3 folder input
s3_folder = st.text_input("Enter S3 folder path", "")

# 2️⃣ Upload Images
uploaded_images = st.file_uploader(
    "Upload cropped images (JPEG)", 
    type=["jpeg"], 
    accept_multiple_files=True
)

# 3️⃣ Upload PDF
uploaded_pdf = st.file_uploader(
    "Upload Maths PDF", 
    type=["pdf"]
)

# 4️⃣ Run Process
if st.button("Process PDF and Upload Images"):
    if not s3_folder:
        st.error("❌ Please enter an S3 folder path")
    elif not uploaded_pdf:
        st.error("❌ Please upload a PDF file")
    else:
        # Save images temporarily
        for img in uploaded_images:
            with open(os.path.join(TEMP_IMAGE_FOLDER, img.name), "wb") as f:
                f.write(img.getbuffer())

        # Save PDF temporarily
        with open(TEMP_PDF_FILE, "wb") as f:
            f.write(uploaded_pdf.getbuffer())

        st.info("⏳ Uploading images to S3...")
        s3_links = upload_images_to_s3(s3_folder)
        st.success(f"✅ Uploaded {len(s3_links)} images to S3")

        st.info("⏳ Processing PDF and attaching images...")
        questions_data = process_maths_pdf(TEMP_PDF_FILE, s3_links)
        st.success(f"✅ Processed PDF! Extracted {len(questions_data)} questions.")

        # Download button
        st.download_button(
            "📥 Download JSON",
            json.dumps(questions_data, indent=4, ensure_ascii=False),
            file_name="maths_questions.json",
            mime="application/json"
        )
