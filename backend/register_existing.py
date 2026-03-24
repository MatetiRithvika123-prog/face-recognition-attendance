import os
import cv2
import numpy as np
import pandas as pd
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import json
from datetime import datetime

# Configure Tesseract path (update this to your Tesseract installation path)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_images_from_pdf(pdf_path, output_dir):
    """Extract images from PDF and save them to output_dir."""
    os.makedirs(output_dir, exist_ok=True)
    doc = fitz.open(pdf_path)
    image_paths = []
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            
            # Save the image
            image_path = os.path.join(output_dir, f"page_{page_num+1}_img_{img_index+1}.jpg")
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            image_paths.append(image_path)
            
    return image_paths

def process_student_images(image_paths, output_dir):
    """Process extracted images to detect and save faces."""
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    student_data = {}
    
    for img_path in image_paths:
        # Read the image
        img = cv2.imread(img_path)
        if img is None:
            continue
            
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_detector.detectMultiScale(gray, 1.3, 5)
        
        # Extract filename without extension
        base_name = os.path.splitext(os.path.basename(img_path))[0]
        
        # Save each face
        for i, (x, y, w, h) in enumerate(faces):
            face_img = img[y:y+h, x:x+w]
            face_filename = f"{base_name}_face_{i+1}.jpg"
            face_path = os.path.join(output_dir, face_filename)
            cv2.imwrite(face_path, face_img)
            
            # Add to student data (you'll need to map this to actual student info)
            student_id = f"{base_name}_{i+1}"
            student_data[student_id] = {
                'image_path': face_path,
                'name': f"Student {len(student_data) + 1}",
                'roll': f"R{1000 + len(student_data) + 1}",
                'branch': 'CSE'  # Default branch, update as needed
            }
    
    return student_data

def train_face_recognizer(student_data, output_dir):
    """Train the face recognizer with the processed faces."""
    face_detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    
    faces = []
    ids = []
    id_count = 0
    student_info = {}
    
    # Create a mapping of student IDs to their information
    for student_id, info in student_data.items():
        img_path = info['image_path']
        if not os.path.exists(img_path):
            print(f"Warning: Image not found: {img_path}")
            continue
            
        # Read and process the image
        img = cv2.imread(img_path)
        if img is None:
            print(f"Warning: Could not read image: {img_path}")
            continue
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        face_rects = face_detector.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
        
        if len(face_rects) == 0:
            print(f"Warning: No face detected in {img_path}")
            continue
            
        # Use the first face found
        (x, y, w, h) = face_rects[0]
        face_img = gray[y:y+h, x:x+w]
        
        # Add to training data
        faces.append(face_img)
        ids.append(id_count)
        
        # Store student information
        student_info[str(id_count)] = {
            'roll': info['roll'],
            'name': info['name'],
            'branch': info['branch']
        }
        
        id_count += 1
    
    # Train the recognizer if we have faces
    if faces:
        recognizer.train(faces, np.array(ids))
        
        # Save the trained model
        os.makedirs("trainer", exist_ok=True)
        recognizer.save(os.path.join("trainer", "trainer.yml"))
        
        # Save student information
        with open(os.path.join("trainer", "student_info.json"), 'w') as f:
            json.dump(student_info, f, indent=2)
        
        print(f"Successfully trained on {len(faces)} face samples from {len(student_info)} students.")
    else:
        print("No valid faces found for training!")

if __name__ == "__main__":
    # Configuration
    pdf_path = r"C:\Users\Mateti\OneDrive\Desktop\rtp\backend\dataset\students.pdf"
    output_dir = os.path.join(os.path.dirname(pdf_path), "extracted_images")
    
    print("Extracting images from PDF...")
    image_paths = extract_images_from_pdf(pdf_path, output_dir)
    print(f"Extracted {len(image_paths)} images from PDF")
    
    print("\nProcessing images to detect faces...")
    student_data = process_student_images(image_paths, output_dir)
    print(f"Processed {len(student_data)} student faces")
    
    print("\nTraining face recognizer...")
    train_face_recognizer(student_data, output_dir)
    
    print("\nProcess completed successfully!")
