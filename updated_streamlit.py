# import streamlit as st
# import os
# import json
# import fitz
# import re
# import cv2
# import numpy as np
# from ultralytics import YOLO
# import boto3
# from botocore.exceptions import NoCredentialsError
# import shutil

# # -------------------- CONFIG --------------------
# TEMP_IMAGE_FOLDER = "temp_images"
# TEMP_PDF_FILE = "temp_pdf.pdf"
# OUTPUT_FOLDER = "output_maths"
# OUTPUT_JSON = os.path.join(OUTPUT_FOLDER, "maths_questions.json")
# CAPTION_DISTANCE = 150
# QUESTION_PATTERN = re.compile(r"^\s*(\d+)\s*[\.\)]")
# YOLO_MODEL_PATH = r"D:\Skillorea_S3\runs\detect\train2\weights\best.pt"

# AWS_ACCESS_KEY_ID = "AKIAS66UDIHPHRDJ2XMP"
# AWS_SECRET_ACCESS_KEY = "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"
# AWS_REGION = "ap-south-1"
# S3_BUCKET_NAME = "studysmartdocuments"

# # -------------------- INITIAL SETUP --------------------
# os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)
# os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# s3_client = boto3.client(
#     "s3",
#     aws_access_key_id=AWS_ACCESS_KEY_ID,
#     aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
#     region_name=AWS_REGION
# )

# # -------------------- HELPER FUNCTIONS --------------------
# def sanitize_filename(name):
#     name = re.sub(r'[\/\\:*?"<>|.]', "", name)
#     name = re.sub(r'[-\s]+', "_", name)
#     return name.strip("_")

# def extract_page_filenames(pdf_path):
#     doc = fitz.open(pdf_path)
#     all_lines = [doc[page_num].get_text().splitlines() for page_num in range(len(doc))]
#     doc.close()
#     first_three = all_lines[0][:3]
#     static_prefix = "_".join(sanitize_filename(line.lower()) for line in first_three if line.strip())
#     page_filenames = [f"{static_prefix}_page_{i+1}.jpeg" for i in range(len(all_lines))]
#     return page_filenames

# def build_global_question_blocks(doc):
#     all_q_blocks = []
#     for page_num in range(len(doc)):
#         page = doc[page_num]
#         text_blocks = page.get_text("blocks")
#         sorted_blocks = sorted(text_blocks, key=lambda b: b[1])
#         for block in sorted_blocks:
#             x1, y1, x2, y2, text, *rest = block
#             for line in text.splitlines():
#                 m = QUESTION_PATTERN.match(line.strip())
#                 if m:
#                     qnum = f"Q{m.group(1)}"
#                     all_q_blocks.append({"page": page_num, "y_top": y1, "y_bottom": y2, "qnum": qnum})
#     return all_q_blocks

# def get_nearest_question(box, all_q_blocks, current_page, max_distance=1000, page_height=842):
#     fy_center = (box[1] + box[3]) / 2
#     min_dist = float("inf")
#     nearest_q = "noQ"
#     # Check above
#     for q in all_q_blocks:
#         if q["page"] > current_page: continue
#         qy_center = (q["y_top"] + q["y_bottom"]) / 2
#         dist = fy_center - qy_center if q["page"] == current_page else fy_center + (current_page - q["page"] - 1) * page_height + (page_height - q["y_bottom"])
#         if 0 <= dist < min_dist and dist < max_distance:
#             min_dist = dist
#             nearest_q = q["qnum"]
#     # Fallback below
#     if nearest_q == "noQ":
#         for q in all_q_blocks:
#             if q["page"] < current_page or q["page"] > current_page + 1: continue
#             qy_center = (q["y_top"] + q["y_bottom"]) / 2
#             dist = qy_center - fy_center if q["page"] == current_page else q["y_top"] + (page_height - fy_center)
#             if 0 <= dist < min_dist and dist < max_distance:
#                 min_dist = dist
#                 nearest_q = q["qnum"]
#     return nearest_q

# def crop_images_from_pdf(pdf_path):
#     model = YOLO(YOLO_MODEL_PATH)
#     doc = fitz.open(pdf_path)
#     page_filenames = extract_page_filenames(pdf_path)
#     all_q_blocks = build_global_question_blocks(doc)
#     page_crop_count = {}
#     cropped_files = []

#     for page_num in range(len(doc)):
#         page = doc[page_num]
#         page_base_name = page_filenames[page_num].replace(".jpeg","")
#         page_height = page.rect.height

#         pix = page.get_pixmap(alpha=False)
#         img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
#         results = model(img)

#         figures, captions, others = [], [], []
#         for r in results:
#             boxes = r.boxes.xyxy.cpu().numpy()
#             classes = r.boxes.cls.cpu().numpy()
#             names = model.names
#             for box, cls in zip(boxes, classes):
#                 label = names[int(cls)]
#                 x1, y1, x2, y2 = map(int, box)
#                 if label == "image-0HH0":
#                     figures.append({"box": (x1,y1,x2,y2), "used": False})
#                 elif label == "caption":
#                     captions.append({"box": (x1,y1,x2,y2), "used": False})
#                 elif label not in ["text", "answer"]:
#                     others.append({"box": (x1,y1,x2,y2), "label": label})

#         # Merge figures and crop
#         for f_idx, fig in enumerate(figures):
#             fx1, fy1, fx2, fy2 = fig["box"]
#             best_caption = None
#             best_distance = 1e9
#             for c_idx, cap in enumerate(captions):
#                 if cap["used"]: continue
#                 cx1, cy1, cx2, cy2 = cap["box"]
#                 dist = max(0, cy1 - fy2) if cy1 >= fy2 else max(0, fy1 - cy2)
#                 if dist < best_distance and dist < CAPTION_DISTANCE:
#                     best_distance = dist
#                     best_caption = (c_idx, cap)
#             merged_box = fig["box"] if not best_caption else (min(fx1, best_caption[1]["box"][0]), min(fy1, best_caption[1]["box"][1]), max(fx2, best_caption[1]["box"][2]), max(fy2, best_caption[1]["box"][3]))
#             crop = img[merged_box[1]:merged_box[3], merged_box[0]:merged_box[2]]
#             crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
#             qnum = get_nearest_question(merged_box, all_q_blocks, page_num, page_height=page_height)
#             page_crop_count[qnum] = page_crop_count.get(qnum,0)+1
#             suffix = f"_{page_crop_count[qnum]}" if page_crop_count[qnum]>1 else ""
#             out_path = os.path.join(TEMP_IMAGE_FOLDER, f"{page_base_name}_{qnum}{suffix}.jpeg")
#             cv2.imwrite(out_path, crop_bgr)
#             cropped_files.append(out_path)
#             if best_caption: captions[best_caption[0]]["used"] = True
#             figures[f_idx]["used"] = True

#     doc.close()
#     return cropped_files

# def upload_images_to_s3(s3_folder):
#     uploaded_links = {}
#     for filename in os.listdir(TEMP_IMAGE_FOLDER):
#         if filename.lower().endswith(".jpeg"):
#             local_path = os.path.join(TEMP_IMAGE_FOLDER, filename)
#             s3_key = f"{s3_folder}/{filename}"
#             try:
#                 s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
#                 file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
#                 q_match = re.search(r'(Q\d+)', filename, re.IGNORECASE)
#                 if q_match: uploaded_links[q_match.group(1).upper()] = file_url
#             except Exception as e:
#                 st.error(f"Upload error: {e}")
#     return uploaded_links

# def refresh_session():
#     for folder in [TEMP_IMAGE_FOLDER, OUTPUT_FOLDER]:
#         if os.path.exists(folder):
#             shutil.rmtree(folder)
#         os.makedirs(folder, exist_ok=True)
#     st.experimental_rerun()

# # -------------------- STREAMLIT UI --------------------
# st.title("📘 Maths Question Processor")

# # Refresh button
# if st.button("🔄 Refresh"):
#     refresh_session()

# # Upload PDF
# uploaded_pdf = st.file_uploader("Upload Maths PDF", type=["pdf"])
# if uploaded_pdf:
#     with open(TEMP_PDF_FILE,"wb") as f:
#         f.write(uploaded_pdf.getbuffer())
#     st.success("✅ PDF uploaded!")

# # Step 1: Crop images
# if uploaded_pdf:
#     if st.button("Crop Images from PDF"):
#         st.info("⏳ Cropping images...")
#         cropped_files = crop_images_from_pdf(TEMP_PDF_FILE)
#         st.success(f"✅ Cropped {len(cropped_files)} images!")
#         for img_file in cropped_files[:5]:  # show first 5 previews
#             st.image(img_file, caption=os.path.basename(img_file), use_column_width=True)
#         st.info("Press 'OK' to proceed to processing.")

# # Step 2: Process PDF + Upload to S3 + JSON
# s3_folder = st.text_input("Enter S3 folder path")
# if st.button("Process PDF and Upload Images") and uploaded_pdf:
#     if not s3_folder: st.error("❌ Enter S3 folder path")
#     else:
#         st.info("⏳ Uploading images to S3...")
#         s3_links = upload_images_to_s3(s3_folder)
#         st.success(f"✅ Uploaded {len(s3_links)} images to S3")
#         # You can integrate your `process_maths_pdf` code here
#         st.success("✅ PDF processed and JSON ready!")


# *********************************************** SOURCE CODE UPDATED ************************************************



import streamlit as st
import os
import json
import fitz  # PyMuPDF
import re
import cv2
import numpy as np
from ultralytics import YOLO
import boto3
from botocore.exceptions import NoCredentialsError
import shutil
from dotenv import load_dotenv

# -------------------- CONFIG --------------------
TEMP_IMAGE_FOLDER = "temp_images"
TEMP_PDF_FILE = "temp_pdf.pdf"
OUTPUT_FOLDER = "output_maths"
OUTPUT_JSON_NN = os.path.join(OUTPUT_FOLDER, "maths_questions_no_newline.json")
OUTPUT_DUP = os.path.join(OUTPUT_FOLDER, "duplicate_output.txt")
CAPTION_DISTANCE = 150
QUESTION_PATTERN = re.compile(r"^\s*(\d+)\s*[\.\)]")
YOLO_MODEL_PATH = r"D:\\Skillorea_S3\\runs\\detect\\train2\\weights\\best.pt"

# AWS_ACCESS_KEY_ID = "AKIAS66UDIHPHRDJ2XMP"
# AWS_SECRET_ACCESS_KEY = "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"
# AWS_REGION = "ap-south-1"
# S3_BUCKET_NAME = "studysmartdocuments"
load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

# -------------------- INITIAL SETUP --------------------
os.makedirs(TEMP_IMAGE_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# -------------------- HELPER FUNCTIONS --------------------
def sanitize_filename(name):
    name = re.sub(r'[\/\\:*?"<>|.]', "", name)
    name = re.sub(r'[-\s]+', "_", name)
    return name.strip("_")

def extract_page_filenames(pdf_path):
    doc = fitz.open(pdf_path)
    all_lines = [doc[page_num].get_text().splitlines() for page_num in range(len(doc))]
    doc.close()
    first_three = all_lines[0][:3]
    static_prefix = "_".join(sanitize_filename(line.lower()) for line in first_three if line.strip())
    page_filenames = [f"{static_prefix}_page_{i+1}.jpeg" for i in range(len(all_lines))]
    return page_filenames

def build_global_question_blocks(doc):
    all_q_blocks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_blocks = page.get_text("blocks")
        sorted_blocks = sorted(text_blocks, key=lambda b: b[1])
        for block in sorted_blocks:
            x1, y1, x2, y2, text, *rest = block
            for line in text.splitlines():
                m = QUESTION_PATTERN.match(line.strip())
                if m:
                    qnum = f"Q{m.group(1)}"
                    all_q_blocks.append({"page": page_num, "y_top": y1, "y_bottom": y2, "qnum": qnum})
    return all_q_blocks

def get_nearest_question(box, all_q_blocks, current_page, max_distance=1000, page_height=842):
    fy_center = (box[1] + box[3]) / 2
    min_dist = float("inf")
    nearest_q = "noQ"
    for q in all_q_blocks:
        if q["page"] > current_page: continue
        qy_center = (q["y_top"] + q["y_bottom"]) / 2
        dist = fy_center - qy_center if q["page"] == current_page else fy_center + (current_page - q["page"] - 1) * page_height + (page_height - q["y_bottom"])
        if 0 <= dist < min_dist and dist < max_distance:
            min_dist = dist
            nearest_q = q["qnum"]
    return nearest_q

def crop_images_from_pdf(pdf_path):
    model = YOLO(YOLO_MODEL_PATH)
    doc = fitz.open(pdf_path)
    page_filenames = extract_page_filenames(pdf_path)
    all_q_blocks = build_global_question_blocks(doc)
    page_crop_count, cropped_files = {}, []

    for page_num in range(len(doc)):
        page = doc[page_num]
        page_base_name = page_filenames[page_num].replace(".jpeg","")
        page_height = page.rect.height
        pix = page.get_pixmap(alpha=False)
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
        results = model(img)

        figures, captions = [], []
        for r in results:
            boxes = r.boxes.xyxy.cpu().numpy()
            classes = r.boxes.cls.cpu().numpy()
            names = model.names
            for box, cls in zip(boxes, classes):
                label = names[int(cls)]
                x1, y1, x2, y2 = map(int, box)
                if label == "image-0HH0":
                    figures.append({"box": (x1,y1,x2,y2)})
                elif label == "caption":
                    captions.append({"box": (x1,y1,x2,y2)})

        for f_idx, fig in enumerate(figures):
            fx1, fy1, fx2, fy2 = fig["box"]
            merged_box = fig["box"]
            crop = img[merged_box[1]:merged_box[3], merged_box[0]:merged_box[2]]
            crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
            qnum = get_nearest_question(merged_box, all_q_blocks, page_num, page_height=page_height)
            page_crop_count[qnum] = page_crop_count.get(qnum,0)+1
            suffix = f"_{page_crop_count[qnum]}" if page_crop_count[qnum]>1 else ""
            out_path = os.path.join(TEMP_IMAGE_FOLDER, f"{page_base_name}_{qnum}{suffix}.jpeg")
            cv2.imwrite(out_path, crop_bgr)
            cropped_files.append((qnum, out_path))

    doc.close()
    return cropped_files

def upload_images_to_s3(cropped_files, s3_folder):
    uploaded_links = {}
    for qnum, local_path in cropped_files:
        filename = os.path.basename(local_path)
        s3_key = f"{s3_folder}/{filename}"
        try:
            s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
            file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
            uploaded_links[qnum] = file_url
        except Exception as e:
            st.error(f"Upload error: {e}")
    return uploaded_links

def remove_explanations_from_questions(lines):
    final_lines, skip_mode, next_question_pattern = [], False, None
    for i, line in enumerate(lines):
        line_stripped = line.strip()
        if skip_mode:
            if next_question_pattern and re.match(next_question_pattern, line_stripped):
                skip_mode = False
                final_lines.append(line)
            continue
        if line_stripped.startswith("Explanation:"):
            skip_mode = True
            for offset in range(i + 1, len(lines)):
                match = re.match(r'^(\d{1,3})\s*\.', lines[offset].strip())
                if match:
                    next_q_num = int(match.group(1))
                    next_question_pattern = rf'^{next_q_num}\s*\.'
                    break
            continue
        final_lines.append(line)
    return final_lines

def get_question_type(q_num):
    if 1 <= q_num <= 150: return "MCQ"
    if 151 <= q_num <= 185: return "ShortAnswer"
    if 186 <= q_num <= 200: return "LongAnswer"
    return "Unknown"

def parse_questions_to_json_structure(lines, s3_links):
    all_questions_data, full_text = [], "\n".join(lines)
    parsed_question_numbers = set()
    question_blocks = re.split(r'\n(?=\s*\d{1,3}\s*\.)', full_text)
    for block in question_blocks:
        block = block.strip()
        if not block: continue
        q_num_match = re.match(r'^\s*(\d{1,3})\s*\.\s*(.*)', block, re.DOTALL)
        if not q_num_match: continue
        q_num = int(q_num_match.group(1))
        if q_num in parsed_question_numbers: continue
        parsed_question_numbers.add(q_num)
        qnum_str = f"Q{q_num}"
        question_type = get_question_type(q_num)
        content_text = q_num_match.group(2).strip()
        question_data = {"questionNUM": qnum_str, "questionType": question_type, "image": s3_links.get(qnum_str)}
        if question_type == "MCQ":
            parts = re.split(r'\nAnswer:\s*', content_text, flags=re.IGNORECASE, maxsplit=1)
            if len(parts) < 2: continue
            question_and_options_part, answer_part = parts
            question_text_lines, options = [], []
            for line in question_and_options_part.split('\n'):
                stripped_line = line.strip()
                if re.match(r'^[A-D]\)\s*', stripped_line):
                    options.append(re.sub(r'^[A-D]\)\s*', '', stripped_line).strip())
                else:
                    question_text_lines.append(line)
            if not options: continue
            question_data["question"] = "\n".join(question_text_lines).strip()
            question_data["options"] = options
            question_data["mark"] = 1
            answer_letter_match = re.search(r'^\s*([A-D])\b', answer_part.strip(), re.IGNORECASE)
            correct_answer_text, correct_option_index = "", None
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
            question_data["correctAnswer"] = correct_answer_text
            question_data["correctOptionIndex"] = correct_option_index
        elif question_type in ["ShortAnswer", "LongAnswer"]:
            keywords_split = re.split(r'\nKeywords:\s*', content_text, flags=re.IGNORECASE, maxsplit=1)
            main_content = keywords_split[0]
            keywords_text = keywords_split[1] if len(keywords_split) > 1 else ""
            answer_split = re.split(r'\nAnswer:\s*', main_content, flags=re.IGNORECASE, maxsplit=1)
            if len(answer_split) < 2: continue
            before_answer_part, answer_part = answer_split
            solution_split = re.split(r'\nSolution:\s*', before_answer_part, flags=re.IGNORECASE, maxsplit=1)
            question_data["question"] = solution_split[0].strip() if len(solution_split) > 1 else before_answer_part.strip()
            question_data["solution"] = solution_split[1].strip() if len(solution_split) > 1 else ""
            question_data["correctAnswer"] = answer_part.strip()
            question_data["answerKeyword"] = [k.strip() for k in keywords_text.split(',') if k.strip()]
            question_data["mark"] = 2 if question_type=="ShortAnswer" else 5
        if "question" in question_data and question_data["question"]:
            all_questions_data.append(question_data)
    return all_questions_data

# -------------------- STREAMLIT UI --------------------
st.set_page_config(page_title="Maths Question Extractor", layout="centered")
st.title("📘 Automated Maths Question Extractor")

if st.button("🔄 Start New Session / Refresh"):
    for folder in [TEMP_IMAGE_FOLDER, OUTPUT_FOLDER]:
        if os.path.exists(folder): shutil.rmtree(folder)
        os.makedirs(folder, exist_ok=True)
    st.experimental_rerun()

st.header("Step 1: Upload PDF")
uploaded_pdf = st.file_uploader("Upload Maths PDF", type=["pdf"])
if uploaded_pdf:
    with open(TEMP_PDF_FILE,"wb") as f: f.write(uploaded_pdf.getbuffer())
    st.success("✅ PDF uploaded successfully!")

st.header("Step 2: Crop Images")
if uploaded_pdf and st.button("🖼️ Crop Images from PDF"):
    st.info("⏳ Cropping images...")
    try:
        cropped_files = crop_images_from_pdf(TEMP_PDF_FILE)
        if cropped_files:
            st.success(f"✅ Cropped {len(cropped_files)} images!")
        else:
            st.warning("⚠️ No images detected.")
    except Exception as e:
        st.error(f"Cropping error: {e}")

st.header("Step 3: Upload to S3 & Generate JSON")
s3_folder = st.text_input("Enter S3 folder path (e.g., maths_documents/class10/ch1)")
if st.button("☁️ Upload Images & Generate JSON") and uploaded_pdf:
    if not s3_folder:
        st.error("❌ Enter S3 folder path.")
    elif not os.listdir(TEMP_IMAGE_FOLDER):
        st.warning("⚠️ No cropped images found.")
    else:
        st.info("⏳ Uploading & Processing...")
        try:
            cropped_files = [(re.search(r'(Q\d+)', f).group(1), os.path.join(TEMP_IMAGE_FOLDER,f)) for f in os.listdir(TEMP_IMAGE_FOLDER) if f.endswith(".jpeg")]
            s3_links = upload_images_to_s3(cropped_files, s3_folder)
            pdf_document = fitz.open(TEMP_PDF_FILE)
            extracted_text = "".join(page.get_text() for page in pdf_document)
            pdf_document.close()
            cleaned_text = re.sub(r'Page\s*\d+', '', extracted_text)
            lines = cleaned_text.splitlines()
            filtered_lines = [line.strip() for line in lines if line.strip() and not re.search(r'(CBSE|GRADE|Chapter|Mathematics)', line, re.IGNORECASE)]
            without_explanations = remove_explanations_from_questions(filtered_lines)
            all_questions = parse_questions_to_json_structure(without_explanations, s3_links)

            # Remove newlines
            def remove_newlines(obj):
                if isinstance(obj, str): return obj.replace("\n"," ").strip()
                if isinstance(obj, list): return [remove_newlines(x) for x in obj]
                if isinstance(obj, dict): return {k: remove_newlines(v) for k,v in obj.items()}
                return obj
            cleaned_questions = remove_newlines(all_questions)

            with open(OUTPUT_JSON_NN, "w", encoding="utf-8") as f: json.dump(cleaned_questions, f, indent=4, ensure_ascii=False)

            # Duplicate report
            qnums = [q["questionNUM"] for q in cleaned_questions]
            duplicates = sorted(set([q for q in qnums if qnums.count(q) > 1]))
            with open(OUTPUT_DUP, "w", encoding="utf-8") as dupf:
                if duplicates:
                    dupf.write("Duplicate Questions Found:\n" + "\n".join(duplicates))
                else:
                    dupf.write("No duplicates found.")

            st.success("✅ JSON + duplicate report generated!")
        except Exception as e:
            st.error(f"Processing error: {e}")

st.header("Step 4: Download Files")
if os.path.exists(OUTPUT_JSON_NN):
    with open(OUTPUT_JSON_NN, "r", encoding="utf-8") as f:
        st.download_button("⬇️ Download JSON File", f.read(), "maths_questions.json", mime="application/json")

if os.path.exists(OUTPUT_DUP):
    with open(OUTPUT_DUP, "r", encoding="utf-8") as f:
        st.download_button("⬇️ Download Duplicates Questions in JSON", f.read(), "duplicate_output.txt", mime="text/plain")



# *********************************************************************
