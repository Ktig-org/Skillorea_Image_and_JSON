import os
import boto3
from botocore.exceptions import NoCredentialsError

# ---------- AWS Credentials ----------
AWS_ACCESS_KEY_ID = "AKIAS66UDIHPHRDJ2XMP"
AWS_SECRET_ACCESS_KEY = "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"
AWS_REGION = "ap-south-1"
S3_BUCKET_NAME = "studysmartdocuments"   # ✅ ONLY bucket name here

# ---------- Local Folder ----------
LOCAL_FOLDER = r"D:\Skillorea_S3\cropped_images"

# ---------- Output File ----------
OUTPUT_FILE = "uploaded_links.txt"

# ---------- Connect to S3 ----------
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_images_to_s3(s3_folder):
    uploaded_links = []
    
    for filename in os.listdir(LOCAL_FOLDER):
        if filename.lower().endswith(".jpeg"):
            local_path = os.path.join(LOCAL_FOLDER, filename)

            # ✅ Use original filename instead of UUID
            s3_key = f"{s3_folder}/{filename}"  

            try:
                # Upload to S3
                s3_client.upload_file(local_path, S3_BUCKET_NAME, s3_key)
                
                # Public URL (bucket policy must allow access)
                file_url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
                uploaded_links.append(file_url)
                print(f"✅ Uploaded: {file_url}")
            
            except FileNotFoundError:
                print(f"❌ File not found: {local_path}")
            except NoCredentialsError:
                print("❌ AWS credentials not available")

    # Save all links to text file
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for link in uploaded_links:
            f.write(link + "\n")

    print(f"\n📄 All uploaded links saved in: {OUTPUT_FILE}")

    return uploaded_links


if __name__ == "__main__":
    # Take folder name from user
    user_input = input("Enter S3 folder path (example: question_collection/2025): ").strip()
    if not user_input:
        print("❌ S3 folder path cannot be empty!")
    else:
        links = upload_images_to_s3(user_input)
