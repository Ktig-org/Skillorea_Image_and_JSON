import fitz  # PyMuPDF
import re
import json
import os
import shutil
import boto3
from botocore.exceptions import NoCredentialsError

# ---------- AWS Credentials ----------
AWS_ACCESS_KEY_ID = "AKIAS66UDIHPHRDJ2XMP"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "ap-south-1"
S3_BUCKET_NAME = "studysmartdocuments"

# ---------- Local Folder ----------
LOCAL_FOLDER = r"D:\Skillorea_S3\cropped_images"
OUTPUT_FILE = "uploaded_links.txt"

# ---------- Connect to S3 ----------
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)


# ------------------- S3 UPLOAD FUNCTION -------------------
def upload_images_to_s3(s3_folder):
    uploaded_links = {}
    for filename in os.listdir(LOCAL_FOLDER):
        if filename.lower().endswith(".jpeg"):
            local_path = os.path.join(LOCAL_FOLDER, filename)
            s3_key = f"{s3_folder}/{filename}"

            try:
                s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
                file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"

                # ✅ Extract Qxxx from filename
                q_match = re.search(r'(Q\d+)', filename, re.IGNORECASE)
                if q_match:
                    q_num = q_match.group(1).upper()
                    uploaded_links[q_num] = file_url

                print(f"✅ Uploaded: {file_url}")

            except FileNotFoundError:
                print(f"❌ File not found: {local_path}")
            except NoCredentialsError:
                print("❌ AWS credentials not available")

    # Save all links
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for q_num, link in uploaded_links.items():
            f.write(f"{q_num} -> {link}\n")

    print(f"\n📄 All uploaded links saved in: {OUTPUT_FILE}")
    return uploaded_links


# ------------------- PDF TO JSON FUNCTION -------------------
def process_maths_pdf(pdf_path, s3_links):
    output_folder = "output_maths"
    json_output_path = os.path.join(output_folder, "maths_questions.json")

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)

    # --- Helper Functions ---
    def get_question_type(q_num):
        if 1 <= q_num <= 150: return "MCQ"
        if 151 <= q_num <= 185: return "ShortAnswer"
        if 186 <= q_num <= 200: return "LongAnswer"
        return "Unknown"

    def clean_text(text: str) -> str:
        """Remove \n and collapse multiple spaces"""
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

            # Base structure
            question_data = {
                "questionNUM": f"Q{q_num}",
                "questionType": question_type,
                "image": None
            }

            # ✅ Attach S3 link if available
            q_key = f"Q{q_num}"
            if q_key in s3_links:
                question_data["image"] = s3_links[q_key]

            # --- Handle MCQ ---
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

                # Correct Answer
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

            # --- Handle Short/Long Answer ---
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

    # --- Extract text from PDF ---
    try:
        pdf_document = fitz.open(pdf_path)
    except FileNotFoundError:
        print(f"❌ PDF not found at '{pdf_path}'")
        return

    extracted_text = "".join(page.get_text() for page in pdf_document)
    pdf_document.close()

    lines = [line.strip() for line in extracted_text.splitlines() if line.strip()]
    all_questions = parse_questions_to_json_structure(lines)

    # Save JSON
    with open(json_output_path, "w", encoding="utf-8") as json_file:
        json.dump(all_questions, json_file, indent=4, ensure_ascii=False)

    print(f"\n✅ Final JSON with images saved at {json_output_path}")


# ------------------- MAIN -------------------
if __name__ == "__main__":
    user_input = input("Enter S3 folder path (example: question_collection/2025/cbse/g7/maths/chapter4images): ").strip()
    if not user_input:
        print("❌ S3 folder path cannot be empty!")
    else:
        # Step 1: Upload images → {Qxxx: link}
        s3_links = upload_images_to_s3(user_input)

        # Step 2: Process PDF → attach images
        pdf_file_path = r"C:\Users\OMEN\Downloads\cbse_math_g7_chapter4_with_keywords.pdf"
        if os.path.exists(pdf_file_path):
            process_maths_pdf(pdf_file_path, s3_links)
        else:
            print(f"❌ PDF not found at '{pdf_file_path}'")
