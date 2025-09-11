# ********************************* BELOW CODE IS FIRST SOURCE CODE OF BAALA IMAGE CROP PROPER NAME ****************************************

# import fitz  # PyMuPDF
# import cv2
# import numpy as np
# from ultralytics import YOLO
# import os
# import re

# # --- Config ---
# pdf_path = r"C:\Users\OMEN\Downloads\cbse_math_g7_chapter7_with_keywords.pdf"
# output_dir = "cropped_images"
# os.makedirs(output_dir, exist_ok=True)
# CAPTION_DISTANCE = 150  # Distance threshold to link caption with image

# # Load YOLO model
# model = YOLO(r"D:\Skillorea_S3\runs\detect\train2\weights\best.pt")

# # --- Helper: sanitize filename ---
# def sanitize_filename(name):
#     # Replace forbidden characters / \ : * ? " < > | . - with underscore
#     name = re.sub(r'[\/\\:*?"<>|.]', "", name)
#     name = re.sub(r'[-\s]+', "_", name)
#     name = name.strip("_")  # remove leading/trailing underscores
#     return name

# # --- Generate page filenames ---
# def extract_page_filenames(pdf_path):
#     doc = fitz.open(pdf_path)
#     all_lines = []

#     # Collect all text from PDF
#     for page_num in range(len(doc)):
#         text = doc[page_num].get_text()
#         all_lines.append(text.splitlines())
#     doc.close()

#     # Use first three lines of first page as static prefix
#     first_three = all_lines[0][:3]
#     static_prefix = "_".join(
#         sanitize_filename(line.lower()) for line in first_three if line.strip()
#     )

#     # Create one filename per page
#     page_filenames = []
#     for i, _ in enumerate(all_lines, 1):
#         page_name = f"{static_prefix}_page_{i}.jpeg"
#         page_filenames.append(page_name)

#     return page_filenames

# # --- Get page filenames ---
# page_filenames = extract_page_filenames(pdf_path)

# # Track counts for multiple crops per page
# page_crop_count = {i: 0 for i in range(len(page_filenames))}

# # --- Open PDF ---
# doc = fitz.open(pdf_path)

# for page_num in range(len(doc)):
#     page = doc[page_num]

#     # Convert PDF page to RGB numpy array
#     pix = page.get_pixmap(alpha=False)
#     img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)

#     # YOLO predictions
#     results = model(img)

#     for r in results:
#         boxes = r.boxes.xyxy.cpu().numpy()
#         classes = r.boxes.cls.cpu().numpy()
#         names = model.names

#         figures, captions, others = [], [], []

#         # Separate detections
#         for (box, cls) in zip(boxes, classes):
#             label = names[int(cls)]
#             x1, y1, x2, y2 = map(int, box)
#             if label == "image-0HH0":
#                 figures.append({"box": (x1, y1, x2, y2), "used": False})
#             elif label == "caption":
#                 captions.append({"box": (x1, y1, x2, y2), "used": False})
#             elif label not in ["text", "answer"]:
#                 others.append({"box": (x1, y1, x2, y2), "label": label})

#         page_base_name = page_filenames[page_num].replace(".jpeg", "")

#         # --- Pair images with captions ---
#         for f_idx, fig in enumerate(figures):
#             fx1, fy1, fx2, fy2 = fig["box"]
#             best_caption = None
#             best_distance = 1e9

#             for c_idx, cap in enumerate(captions):
#                 if cap["used"]:
#                     continue
#                 cx1, cy1, cx2, cy2 = cap["box"]
#                 # distance between figure and caption
#                 if cy1 >= fy2:
#                     dist = cy1 - fy2
#                 elif cy2 <= fy1:
#                     dist = fy1 - cy2
#                 else:
#                     dist = 0
#                 if dist < best_distance and dist < CAPTION_DISTANCE:
#                     best_distance = dist
#                     best_caption = (c_idx, cap)

#             if best_caption:
#                 c_idx, cap = best_caption
#                 cx1, cy1, cx2, cy2 = cap["box"]

#                 merged_box = (
#                     min(fx1, cx1),
#                     min(fy1, cy1),
#                     max(fx2, cx2),
#                     max(fy2, cy2),
#                 )
#                 crop = img[merged_box[1]:merged_box[3], merged_box[0]:merged_box[2]]
#                 crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)

#                 page_crop_count[page_num] += 1
#                 suffix = f"_{page_crop_count[page_num]}" if page_crop_count[page_num] > 1 else ""
#                 out_path = os.path.join(output_dir, f"{page_base_name}{suffix}.jpeg")
#                 cv2.imwrite(out_path, crop_bgr)
#                 print(f"Saved: {out_path}")

#                 captions[c_idx]["used"] = True
#                 figures[f_idx]["used"] = True

#         # --- Save standalone images ---
#         for f_idx, fig in enumerate(figures):
#             if not fig["used"]:
#                 x1, y1, x2, y2 = fig["box"]
#                 crop = img[y1:y2, x1:x2]
#                 crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)

#                 page_crop_count[page_num] += 1
#                 suffix = f"_{page_crop_count[page_num]}" if page_crop_count[page_num] > 1 else ""
#                 out_path = os.path.join(output_dir, f"{page_base_name}{suffix}.jpeg")
#                 cv2.imwrite(out_path, crop_bgr)
#                 print(f"Saved: {out_path}")

#         # --- Save other objects ---
#         for o_idx, obj in enumerate(others):
#             x1, y1, x2, y2 = obj["box"]
#             crop = img[y1:y2, x1:x2]
#             crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)

#             page_crop_count[page_num] += 1
#             suffix = f"_{page_crop_count[page_num]}" if page_crop_count[page_num] > 1 else ""
#             out_path = os.path.join(output_dir, f"{page_base_name}{suffix}.jpeg")
#             cv2.imwrite(out_path, crop_bgr)
#             print(f"Saved: {out_path}")

# doc.close()

# **************************************** ABOVE CODE IS FIRST SOURCE CODE OF BAALA IMAGE CROP PROPER NAME ****************************************


# **************************************** SHILPA MA'AM CODE BELOW - IMAGE CROP CODE WITH PROPER NAME ****************************************

import fitz  # PyMuPDF
import cv2
import numpy as np
from ultralytics import YOLO
import pytesseract
import os
import re
 
# --- Config ---
pdf_path = r"C:\Users\OMEN\Downloads\CBSE GRADE 6 MATHS CHAPTER 1 (KEY).pdf"
output_dir = "cropped_images"
os.makedirs(output_dir, exist_ok=True)
CAPTION_DISTANCE = 150  # Distance threshold to link caption with image
# pytesseract.pytesseract.tesseract_cmd = "/opt/homebrew/bin/tesseract"
 
# Regex to detect question numbers
QUESTION_PATTERN = re.compile(r"^\s*(\d+)\s*[\.\)]")
 
# Load YOLO model
model = YOLO(r"D:\Skillorea_S3\runs\detect\train2\weights\best.pt")
 
# --- Helper functions ---
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
 
# --- Build global question blocks across all pages ---
def build_global_question_blocks(doc):
    all_q_blocks = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text_blocks = page.get_text("blocks")  # list of (x1,y1,x2,y2,text,...)
        sorted_blocks = sorted(text_blocks, key=lambda b: b[1])
        for block in sorted_blocks:
            x1, y1, x2, y2, text, *rest = block
            for line in text.splitlines():
                m = QUESTION_PATTERN.match(line.strip())
                if m:
                    qnum = f"Q{m.group(1)}"
                    all_q_blocks.append({
                        "page": page_num,
                        "y_top": y1,
                        "y_bottom": y2,
                        "qnum": qnum
                    })
    return all_q_blocks
 
# --- Get nearest question for a figure ---
def get_nearest_question(box, all_q_blocks, current_page, max_distance=1000, page_height=842):
    fy_center = (box[1] + box[3]) / 2  # Center y of figure
    min_dist = float("inf")
    nearest_q = "noQ"
 
    # Step 1: Look for questions above the figure on the same or previous pages
    for q in all_q_blocks:
        if q["page"] > current_page:  # Skip questions from future pages
            continue
        if q["page"] == current_page:
            qy_center = (q["y_top"] + q["y_bottom"]) / 2
            dist = fy_center - qy_center  # Positive if question is above
        else:  # Previous page
            dist = fy_center + (current_page - q["page"] - 1) * page_height + (page_height - q["y_bottom"])
        if 0 <= dist < min_dist and dist < max_distance:
            min_dist = dist
            nearest_q = q["qnum"]
 
    # Step 2: Fallback to questions below on the same page or next page only
    if nearest_q == "noQ":
        for q in all_q_blocks:
            if q["page"] < current_page or q["page"] > current_page + 1:  # Limit to same or next page
                continue
            if q["page"] == current_page:
                qy_center = (q["y_top"] + q["y_bottom"]) / 2
                dist = qy_center - fy_center  # Positive if question is below
            else:  # Next page
                dist = q["y_top"] + (page_height - fy_center)
            if 0 <= dist < min_dist and dist < max_distance:
                min_dist = dist
                nearest_q = q["qnum"]
 
    return nearest_q
 
# --- Prepare ---
doc = fitz.open(pdf_path)
page_filenames = extract_page_filenames(pdf_path)
all_q_blocks = build_global_question_blocks(doc)
page_crop_count = {}  # to track multiple images per question globally
 
# --- Process pages ---
for page_num in range(len(doc)):
    page = doc[page_num]
    page_base_name = page_filenames[page_num].replace(".jpeg", "")
    page_height = page.rect.height  # Get actual page height
 
    # Convert page to image
    pix = page.get_pixmap(alpha=False)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)
 
    # YOLO detection
    results = model(img)
    figures, captions, others = [], [], []
 
    for r in results:
        boxes = r.boxes.xyxy.cpu().numpy()
        classes = r.boxes.cls.cpu().numpy()
        names = model.names
 
        for box, cls in zip(boxes, classes):
            label = names[int(cls)]
            x1, y1, x2, y2 = map(int, box)
            if label == "image-0HH0":
                figures.append({"box": (x1, y1, x2, y2), "used": False})
            elif label == "caption":
                captions.append({"box": (x1, y1, x2, y2), "used": False})
            elif label not in ["text", "answer"]:
                others.append({"box": (x1, y1, x2, y2), "label": label})
 
    # Merge figures with captions
    for f_idx, fig in enumerate(figures):
        fx1, fy1, fx2, fy2 = fig["box"]
        best_caption = None
        best_distance = 1e9
        for c_idx, cap in enumerate(captions):
            if cap["used"]:
                continue
            cx1, cy1, cx2, cy2 = cap["box"]
            dist = max(0, cy1 - fy2) if cy1 >= fy2 else max(0, fy1 - cy2)
            if dist < best_distance and dist < CAPTION_DISTANCE:
                best_distance = dist
                best_caption = (c_idx, cap)
 
        if best_caption:
            c_idx, cap = best_caption
            merged_box = (
                min(fx1, cap["box"][0]),
                min(fy1, cap["box"][1]),
                max(fx2, cap["box"][2]),
                max(fy2, cap["box"][3])
            )
        else:
            merged_box = fig["box"]
 
        # Crop
        crop = img[merged_box[1]:merged_box[3], merged_box[0]:merged_box[2]]
        crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
 
        # Assign question number
        qnum = get_nearest_question(merged_box, all_q_blocks, page_num, max_distance=1000, page_height=page_height)
        if qnum not in page_crop_count:
            page_crop_count[qnum] = 0
        page_crop_count[qnum] += 1
        suffix = f"_{page_crop_count[qnum]}" if page_crop_count[qnum] > 1 else ""
        out_path = os.path.join(output_dir, f"{page_base_name}_{qnum}{suffix}.jpeg")
        cv2.imwrite(out_path, crop_bgr)
        print(f"Saved: {out_path}")
 
        if best_caption:
            captions[c_idx]["used"] = True
        figures[f_idx]["used"] = True
 
    # Save remaining standalone figures
    for f_idx, fig in enumerate(figures):
        if not fig["used"]:
            x1, y1, x2, y2 = fig["box"]
            crop = img[y1:y2, x1:x2]
            crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
            qnum = get_nearest_question(fig["box"], all_q_blocks, page_num, max_distance=1000, page_height=page_height)
            if qnum not in page_crop_count:
                page_crop_count[qnum] = 0
            page_crop_count[qnum] += 1
            suffix = f"_{page_crop_count[qnum]}" if page_crop_count[qnum] > 1 else ""
            out_path = os.path.join(output_dir, f"{page_base_name}_{qnum}{suffix}.jpeg")
            cv2.imwrite(out_path, crop_bgr)
            print(f"Saved: {out_path}")
 
    # Save other objects if needed
    for obj in others:
        x1, y1, x2, y2 = obj["box"]
        crop = img[y1:y2, x1:x2]
        crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
        qnum = get_nearest_question(obj["box"], all_q_blocks, page_num, max_distance=1000, page_height=page_height)
        if qnum not in page_crop_count:
            page_crop_count[qnum] = 0
        page_crop_count[qnum] += 1
        suffix = f"_{page_crop_count[qnum]}" if page_crop_count[qnum] > 1 else ""
        out_path = os.path.join(output_dir, f"{page_base_name}_{qnum}{suffix}.jpeg")
        cv2.imwrite(out_path, crop_bgr)
        print(f"Saved: {out_path}")
 
doc.close()

# **************************************** ABOVE CODE IS SHILPA MA'AM IMAGE CROP CODE WITH PROPER NAME ****************************************


# **************************************** MUGUNTH CODE BELOW - JSON WITH "\n" ****************************************

# import fitz  # PyMuPDF
# import re    # Regular expression module
# import json  # JSON module for output
# import os    # For path and directory operations
# import shutil # For removing directory trees

# def process_maths_pdf(pdf_path):
#     """
#     Processes a mathematics PDF to extract questions into a structured JSON file
#     and generate a report on any duplicate questions found.

#     The entire process is self-contained, creating an 'output_maths' folder
#     for the final files.
#     """
#     # --- 1. Setup Output Directory ---
#     output_folder = "output_maths"
#     json_output_path = os.path.join(output_folder, "maths_questions.json")
#     duplicate_output_path = os.path.join(output_folder, "duplicate_output.txt")

#     if os.path.exists(output_folder):
#         shutil.rmtree(output_folder)
#     os.makedirs(output_folder, exist_ok=True)
    
#     # --- 2. Nested Helper Functions for PDF Parsing and Cleaning ---
    
#     def remove_explanations_from_questions(lines):
#         final_lines = []
#         skip_mode = False
#         next_question_pattern = None
#         for i, line in enumerate(lines):
#             line_stripped = line.strip()
#             if skip_mode:
#                 if next_question_pattern and re.match(next_question_pattern, line_stripped):
#                     skip_mode = False
#                     final_lines.append(line)
#                 continue
#             if line_stripped.startswith("Explanation:"):
#                 skip_mode = True
#                 for offset in range(i + 1, len(lines)):
#                     match = re.match(r'^(\d{1,3})\s*\.', lines[offset].strip())
#                     if match:
#                         next_q_num = int(match.group(1))
#                         next_question_pattern = rf'^{next_q_num}\s*\.'
#                         break
#                 continue
#             final_lines.append(line)
#         return final_lines

#     # This function is no longer called, as keywords are now parsed.
#     # It is kept here to minimize structural changes to the original file.
#     def remove_keywords_from_questions(lines):
#         final_lines = []
#         skip_mode = False
#         next_question_pattern = None
#         for i, line in enumerate(lines):
#             line_stripped = line.strip()
#             if skip_mode:
#                 if next_question_pattern and re.match(next_question_pattern, line_stripped):
#                     skip_mode = False
#                     final_lines.append(line)
#                 continue
#             if line_stripped.startswith("Keywords:"):
#                 skip_mode = True
#                 for offset in range(i + 1, len(lines)):
#                     match = re.match(r'^(\d{1,3})\s*\.', lines[offset].strip())
#                     if match:
#                         next_q_num = int(match.group(1))
#                         next_question_pattern = rf'^{next_q_num}\s*\.'
#                         break
#                 continue
#             final_lines.append(line)
#         return final_lines

#     def get_question_type(q_num):
#         if 1 <= q_num <= 150: return "MCQ"
#         if 151 <= q_num <= 185: return "ShortAnswer"
#         if 186 <= q_num <= 200: return "LongAnswer"
#         return "Unknown"

#     def parse_questions_to_json_structure(lines):
#         all_questions_data = []
#         full_text = "\n".join(lines)
#         parsed_question_numbers = set()
#         question_blocks = re.split(r'\n(?=\s*\d{1,3}\s*\.)', full_text)

#         for block in question_blocks:
#             block = block.strip()
#             if not block: continue
            
#             q_num_match = re.match(r'^\s*(\d{1,3})\s*\.\s*(.*)', block, re.DOTALL)
#             if not q_num_match: continue
            
#             q_num = int(q_num_match.group(1))
#             if q_num in parsed_question_numbers:
#                 continue
#             parsed_question_numbers.add(q_num)
            
#             question_type = get_question_type(q_num)
#             content_text = q_num_match.group(2).strip()
#             question_data = {"questionNUM": f"pdf_{q_num}", "questionType": question_type, "image": None}

#             if question_type == "MCQ":
#                 parts = re.split(r'\nAnswer:\s*', content_text, flags=re.IGNORECASE, maxsplit=1)
#                 if len(parts) < 2: continue
                
#                 question_and_options_part, answer_part = parts
#                 question_text_lines, options = [], []
                
#                 for line in question_and_options_part.split('\n'):
#                     stripped_line = line.strip()
#                     if re.match(r'^[A-D]\)\s*', stripped_line):
#                         options.append(re.sub(r'^[A-D]\)\s*', '', stripped_line).strip())
#                     else:
#                         question_text_lines.append(line)
                
#                 if not options: continue
                
#                 question_data["question"] = "\n".join(question_text_lines).strip()
#                 question_data["options"] = options
#                 question_data["mark"] = 1

#                 answer_letter_match = re.search(r'^\s*([A-D])\b', answer_part.strip(), re.IGNORECASE)
#                 correct_answer_text = ""
#                 correct_option_index = None

#                 if answer_letter_match:
#                     answer_letter = answer_letter_match.group(1).upper()
#                     idx = ord(answer_letter) - ord('A')
#                     if 0 <= idx < len(options):
#                         correct_answer_text = options[idx]
#                         correct_option_index = idx + 1
                
#                 if not correct_answer_text:
#                     cleaned_answer = re.sub(r'^[A-D]\)\s*', '', answer_part.strip()).strip()
#                     correct_answer_text = cleaned_answer
#                     if cleaned_answer in options:
#                         correct_option_index = options.index(cleaned_answer)

#                 question_data["correctAnswer"] = correct_answer_text
#                 question_data["correctOptionIndex"] = correct_option_index

#             elif question_type in ["ShortAnswer", "LongAnswer"]:
#                 keywords_split = re.split(r'\nKeywords:\s*', content_text, flags=re.IGNORECASE, maxsplit=1)
#                 main_content = keywords_split[0]
#                 keywords_text = keywords_split[1] if len(keywords_split) > 1 else ""

#                 answer_split = re.split(r'\nAnswer:\s*', main_content, flags=re.IGNORECASE, maxsplit=1)
#                 if len(answer_split) < 2: continue
                
#                 before_answer_part, answer_part = answer_split
#                 solution_split = re.split(r'\nSolution:\s*', before_answer_part, flags=re.IGNORECASE, maxsplit=1)
                
#                 question_data["question"] = solution_split[0].strip() if len(solution_split) > 1 else before_answer_part.strip()
#                 question_data["solution"] = solution_split[1].strip() if len(solution_split) > 1 else ""
#                 question_data["correctAnswer"] = answer_part.strip()
#                 question_data["answerKeyword"] = [k.strip() for k in keywords_text.split(',') if k.strip()]

#                 if question_type == "ShortAnswer":
#                     question_data["mark"] = 2
#                 elif question_type == "LongAnswer":
#                     question_data["mark"] = 5
            
#             if "question" in question_data and question_data["question"]:
#                 all_questions_data.append(question_data)

#         return all_questions_data

#     # --- 3. Main PDF Processing Logic ---
#     try:
#         pdf_document = fitz.open(pdf_path)
#     # === THIS IS THE CORRECTED LINE ===
#     except FileNotFoundError:
#         print(f"Error: The file '{pdf_path}' was not found.")
#         return

#     extracted_text = "".join(page.get_text() for page in pdf_document)
#     pdf_document.close()

#     cleaned_text = re.sub(r'Page\s*\d+', '', extracted_text)
#     lines = cleaned_text.splitlines()

#     filtered_lines = [
#         line.strip() for line in lines if line.strip() and
#         not (re.search(r'CBSE', line, re.IGNORECASE) and re.search(r'GRADE', line, re.IGNORECASE)) and
#         not re.search(r'Chapter\s*\d{1,2}', line, re.IGNORECASE) and
#         not re.search(r'Mathematics', line, re.IGNORECASE)
#     ]

#     without_explanations = remove_explanations_from_questions(filtered_lines)
#     # The call to remove_keywords_from_questions is removed to allow keyword parsing.
#     all_questions = parse_questions_to_json_structure(without_explanations)

#     # --- New section to re-order keys for clean JSON output ---
#     ordered_questions = []
#     for q in all_questions:
#         q_type = q.get("questionType")
#         ordered_q = {}

#         if q_type == "MCQ":
#             ordered_q = {
#                 "questionNUM": q.get("questionNUM"),
#                 "question": q.get("question"),
#                 "questionType": q_type,
#                 "image": q.get("image"),
#                 "options": q.get("options"),
#                 "correctOptionIndex": q.get("correctOptionIndex"),
#                 "correctAnswer": q.get("correctAnswer"),
#                 "mark": q.get("mark")
#             }
#         elif q_type in ["ShortAnswer", "LongAnswer"]:
#             ordered_q = {
#                 "questionNUM": q.get("questionNUM"),
#                 "question": q.get("question"),
#                 "questionType": q_type,
#                 "image": q.get("image"),
#                 "solution": q.get("solution"),
#                 "correctAnswer": q.get("correctAnswer"),
#                 "answerKeyword": q.get("answerKeyword"),
#                 "mark": q.get("mark")
#             }
#         else: # Fallback for any unexpected types
#             ordered_q = q
        
#         ordered_questions.append(ordered_q)

#     with open(json_output_path, "w", encoding="utf-8") as json_file:
#         json.dump(ordered_questions, json_file, indent=4, ensure_ascii=False)

#     # --- 4. Duplicate Checking Logic (using the ordered list for consistency) ---
#     def normalize_question_text(text):
#         return re.sub(r'\s+', '', text.lower()) if isinstance(text, str) else ""

#     def count_option_mismatches(opt1, opt2):
#         s1 = set(map(str, opt1)) if isinstance(opt1, list) else set()
#         s2 = set(map(str, opt2)) if isinstance(opt2, list) else set()
#         return len(s1.symmetric_difference(s2))

#     seen, reports, dup_count = {}, [], 0
#     for item in ordered_questions:
#         norm = normalize_question_text(item.get("question", ""))
#         if not norm:
#             continue
#         if norm in seen:
#             dup_count += 1
#             orig = seen[norm]
#             mismatch = []
#             if item.get("questionType") != orig.get("questionType"):
#                 mismatch.append("questionType mismatch")
#             if str(item.get("correctAnswer")) != str(orig.get("correctAnswer")):
#                 mismatch.append("correctAnswer mismatch")
#             if str(item.get("solution")) != str(orig.get("solution")):
#                 mismatch.append("solution mismatch")
#             if item.get("questionType", "").lower() == "mcq":
#                 mismatch.append(f"{count_option_mismatches(item.get('options'), orig.get('options'))} options mismatched")
#             summary = f"DUPLICATE {dup_count}: {item['questionNUM']} duplicates {orig['questionNUM']} - {', '.join(mismatch) or 'all fields match'}"
#             reports.append(f"{summary}\n\nOriginal:\n{json.dumps(orig, indent=4)}\n\nDuplicate:\n{json.dumps(item, indent=4)}\n{'='*70}\n")
#         else:
#             seen[norm] = item

#     with open(duplicate_output_path, "w", encoding="utf-8") as f:
#         if reports:
#             f.write(f"Found {dup_count} duplicate entries.\n{'='*70}\n\n" + "\n".join(reports))
#         else:
#             f.write("No duplicates found.\n")

#     print(f"\n✅ Extracted questions to {json_output_path}")
#     print(f"✅ Duplicate report saved to {duplicate_output_path}")

# # --- Example Usage ---
# if __name__ == "__main__":
#     # IMPORTANT: Replace this with the actual path to your PDF file
#     pdf_file_path = r"C:\Users\OMEN\Downloads\cbse_math_g7_chapter4_with_keywords.pdf" #r"E:\SUBJECTS_PDF\AI\MATHS\CBSE GRADE 6 MATHS CHAPTER 1 (KEY).pdf"
#     if os.path.exists(pdf_file_path):
#         process_maths_pdf(pdf_file_path)
#     else:
#         print(f"Error: The specified PDF file does not exist at '{pdf_file_path}'")
#         print("Please update the 'pdf_file_path' variable in the `if __name__ == '__main__':` block.")

# **************************************** MUGUNTH CODE ABOVE - JSON WITH "\n" ****************************************

# **************************************** MUGUNTH CODE BELOW - JSON WITHOUT "\n" CLEAN JSON ****************************************

import fitz  # PyMuPDF
import re    # Regular expression module
import json  # JSON module for output
import os    # For path and directory operations
import shutil # For removing directory trees

def process_maths_pdf(pdf_path):
    """
    Processes a mathematics PDF to extract questions into structured JSON files
    and generate a report on any duplicate questions found.

    Outputs:
      - maths_questions.json (with original formatting)
      - maths_questions_no_newline.json (all '\n' removed)
      - duplicate_output.txt (duplicate report)
    """
    # --- 1. Setup Output Directory ---
    output_folder = "output_maths"
    json_output_path = os.path.join(output_folder, "maths_questions.json")
    json_no_newline_path = os.path.join(output_folder, "maths_questions_no_newline.json")
    duplicate_output_path = os.path.join(output_folder, "duplicate_output.txt")

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.makedirs(output_folder, exist_ok=True)
    
    # --- 2. Nested Helper Functions for PDF Parsing and Cleaning ---
    def remove_explanations_from_questions(lines):
        final_lines = []
        skip_mode = False
        next_question_pattern = None
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

    def parse_questions_to_json_structure(lines):
        all_questions_data = []
        full_text = "\n".join(lines)
        parsed_question_numbers = set()
        question_blocks = re.split(r'\n(?=\s*\d{1,3}\s*\.)', full_text)

        for block in question_blocks:
            block = block.strip()
            if not block: continue
            
            q_num_match = re.match(r'^\s*(\d{1,3})\s*\.\s*(.*)', block, re.DOTALL)
            if not q_num_match: continue
            
            q_num = int(q_num_match.group(1))
            if q_num in parsed_question_numbers:
                continue
            parsed_question_numbers.add(q_num)
            
            question_type = get_question_type(q_num)
            content_text = q_num_match.group(2).strip()
            question_data = {"questionNUM": f"Q{q_num}", "questionType": question_type, "image": None}

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
                correct_answer_text = ""
                correct_option_index = None

                if answer_letter_match:
                    answer_letter = answer_letter_match.group(1).upper()
                    idx = ord(answer_letter) - ord('A')
                    if 0 <= idx < len(options):
                        correct_answer_text = options[idx]
                        correct_option_index = idx + 1
                
                if not correct_answer_text:
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

                if question_type == "ShortAnswer":
                    question_data["mark"] = 2
                elif question_type == "LongAnswer":
                    question_data["mark"] = 5
            
            if "question" in question_data and question_data["question"]:
                all_questions_data.append(question_data)

        return all_questions_data

    # --- 3. Main PDF Processing Logic ---
    try:
        pdf_document = fitz.open(pdf_path)
    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
        return

    extracted_text = "".join(page.get_text() for page in pdf_document)
    pdf_document.close()

    cleaned_text = re.sub(r'Page\s*\d+', '', extracted_text)
    lines = cleaned_text.splitlines()

    filtered_lines = [
        line.strip() for line in lines if line.strip() and
        not (re.search(r'CBSE', line, re.IGNORECASE) and re.search(r'GRADE', line, re.IGNORECASE)) and
        not re.search(r'Chapter\s*\d{1,2}', line, re.IGNORECASE) and
        not re.search(r'Mathematics', line, re.IGNORECASE)
    ]

    without_explanations = remove_explanations_from_questions(filtered_lines)
    all_questions = parse_questions_to_json_structure(without_explanations)

    # --- Re-order keys for clean JSON output ---
    ordered_questions = []
    for q in all_questions:
        q_type = q.get("questionType")
        ordered_q = {}

        if q_type == "MCQ":
            ordered_q = {
                "questionNUM": q.get("questionNUM"),
                "question": q.get("question"),
                "questionType": q_type,
                "image": q.get("image"),
                "options": q.get("options"),
                "correctOptionIndex": q.get("correctOptionIndex"),
                "correctAnswer": q.get("correctAnswer"),
                "mark": q.get("mark")
            }
        elif q_type in ["ShortAnswer", "LongAnswer"]:
            ordered_q = {
                "questionNUM": q.get("questionNUM"),
                "question": q.get("question"),
                "questionType": q_type,
                "image": q.get("image"),
                "solution": q.get("solution"),
                "correctAnswer": q.get("correctAnswer"),
                "answerKeyword": q.get("answerKeyword"),
                "mark": q.get("mark")
            }
        else:
            ordered_q = q
        
        ordered_questions.append(ordered_q)

    # Save original JSON (with \n)
    with open(json_output_path, "w", encoding="utf-8") as json_file:
        json.dump(ordered_questions, json_file, indent=4, ensure_ascii=False)

    # --- 4A. Create JSON without "\n" ---
    def remove_newlines(obj):
        if isinstance(obj, str):
            return obj.replace("\n", " ").strip()
        elif isinstance(obj, list):
            return [remove_newlines(x) for x in obj]
        elif isinstance(obj, dict):
            return {k: remove_newlines(v) for k, v in obj.items()}
        return obj

    cleaned_questions = remove_newlines(ordered_questions)
    with open(json_no_newline_path, "w", encoding="utf-8") as json_file:
        json.dump(cleaned_questions, json_file, indent=4, ensure_ascii=False)

    # --- 4B. Duplicate Checking Logic ---
    def normalize_question_text(text):
        return re.sub(r'\s+', '', text.lower()) if isinstance(text, str) else ""

    def count_option_mismatches(opt1, opt2):
        s1 = set(map(str, opt1)) if isinstance(opt1, list) else set()
        s2 = set(map(str, opt2)) if isinstance(opt2, list) else set()
        return len(s1.symmetric_difference(s2))

    seen, reports, dup_count = {}, [], 0
    for item in ordered_questions:
        norm = normalize_question_text(item.get("question", ""))
        if not norm:
            continue
        if norm in seen:
            dup_count += 1
            orig = seen[norm]
            mismatch = []
            if item.get("questionType") != orig.get("questionType"):
                mismatch.append("questionType mismatch")
            if str(item.get("correctAnswer")) != str(orig.get("correctAnswer")):
                mismatch.append("correctAnswer mismatch")
            if str(item.get("solution")) != str(orig.get("solution")):
                mismatch.append("solution mismatch")
            if item.get("questionType", "").lower() == "mcq":
                mismatch.append(f"{count_option_mismatches(item.get('options'), orig.get('options'))} options mismatched")
            summary = f"DUPLICATE {dup_count}: {item['questionNUM']} duplicates {orig['questionNUM']} - {', '.join(mismatch) or 'all fields match'}"
            reports.append(f"{summary}\n\nOriginal:\n{json.dumps(orig, indent=4)}\n\nDuplicate:\n{json.dumps(item, indent=4)}\n{'='*70}\n")
        else:
            seen[norm] = item

    with open(duplicate_output_path, "w", encoding="utf-8") as f:
        if reports:
            f.write(f"Found {dup_count} duplicate entries.\n{'='*70}\n\n" + "\n".join(reports))
        else:
            f.write("No duplicates found.\n")

    print(f"\n✅ Extracted questions to {json_output_path}")
    print(f"✅ Clean JSON without '\\n' saved to {json_no_newline_path}")
    print(f"✅ Duplicate report saved to {duplicate_output_path}")

# --- Example Usage ---
if __name__ == "__main__":
    # Replace with actual PDF path
    pdf_file_path = r"C:\Users\OMEN\Downloads\cbse_math_g7_chapter4_with_keywords.pdf"
    if os.path.exists(pdf_file_path):
        process_maths_pdf(pdf_file_path)
    else:
        print(f"Error: The specified PDF file does not exist at '{pdf_file_path}'")

# **************************************** MUGUNTH CODE ABOVE - JSON WITHOUT "\n" CLEAN JSON ****************************************