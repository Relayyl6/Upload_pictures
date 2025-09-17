from flask import Flask, redirect, render_template, flash, send_file, jsonify, request
import os
from PIL import Image
from flask_cors import CORS
import uuid
import shutil
import cv2
import numpy as np
from werkzeug.utils import secure_filename
import atexit
from zipfile import ZipFile

app = Flask(__name__)
CORS(app)

# this is not a real key
# API_KEY = '12345abcXYZ'
HOME_DIR = os.path.expanduser("~")
UPLOAD_DIR = os.path.join(HOME_DIR, "Downloads", "upload")
OUTPUT_DIR = os.path.join(HOME_DIR, "Downloads", "output")
# UPLOAD_DIR = '/upload'
# OUTPUT_DIR = '/output'
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
app.config['SECRET_KEY'] = 'your-secure-random-secret-key-1234567890'

def apply_black_and_white(image):
    return image.convert("L")

def apply_cartoon(image):
    # Loading the image
    im = np.array(image)

    if im is None:
        raise ValueError(f"Failed to load image: {image}") 

    # Edge detection
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    # Color quantization
    color = cv2.bilateralFilter(im, 9, 250, 250)

    # Combine edges and colors
    cartoon = cv2.bitwise_and(color, color, mask=edges)
    return cartoon

def apply_sepia(image):
    image_array = np.array(image)
    if image_array.shape[2] != 3:  # Ensure image is RGB
        raise ValueError("Image must be in RGB format")
    
    sepia_matrix = np.array([
        [0.393, 0.769, 0.189],
        [0.349, 0.686, 0.168],
        [0.272, 0.534, 0.131],
    ])
    reshaped_image = image_array.reshape(-1, 3)
    sepia_reshaped = reshaped_image.dot(sepia_matrix.T) # .T for transpose of the matrix
    # Clip values to the valid range [0, 255]
    sepia_reshaped = np.clip(sepia_reshaped, 0, 255)
    # Reshape back to the original image dimensions
    return sepia_reshaped.reshape(image_array.shape).astype(np.uint8)


@app.route("/")
def input():
    return render_template('Temp.html')

@app.route('/upload', methods= ['POST'])
def upload():
    try:
        #creating a unique session
        # uuid = uuid.uuid4()
        session_id = str(uuid.uuid4());
        session_dir = os.path.join(OUTPUT_DIR, session_id)
        sepia_dir = os.path.join(session_dir, 'sepia')
        black_and_white_dir = os.path.join(session_dir, 'BW')
        cartoon_dir = os.path.join(session_dir, 'cartoon')
        os.makedirs(sepia_dir, exist_ok=True)
        os.makedirs(black_and_white_dir, exist_ok=True)
        os.makedirs(cartoon_dir, exist_ok=True)

        if "image" not in request.files:
            flash('No file part')
            return jsonify({"error": "No file part in the request"}), 400
        
        images = request.files.getlist("image")

        if not images or all(image.filename == "" for image in images):
            return jsonify({"error": "No valid files uploaded"}), 400

        for image_file in images:
            if image_file.filename == '':
                flash("No selected file")
                return redirect(request.url)
            filename = secure_filename(image_file.filename)
            if filename != '':
                file_ext = os.path.splitext(filename)[1]
                if file_ext.lower() not in ALLOWED_EXTENSIONS:
                    flash("File type not allowed")
                    return redirect(request.url)

                # save file to path of image
                image_file_path = os.path.join(UPLOAD_DIR, filename)
                image_file.save(image_file_path)

                # open file with pillow and convert any uploaded to an RGB format
                im = Image.open(image_file_path).convert('RGB')

                # applying edits
                black_and_white_image = apply_black_and_white(im)
                cartoon_image = Image.fromarray(apply_cartoon(im))
                sepia_image = Image.fromarray(apply_sepia(im))

                # joining edited images to the respective directory
                bw_file_path = os.path.join(black_and_white_dir, filename)
                print(f"Saved B/W image to {os.path.join(black_and_white_dir, filename)}")
                sp_file_path = os.path.join(sepia_dir, filename)
                print(f"Saved sepia image to {os.path.join(sepia_dir, filename)}")
                ct_file_path = os.path.join(cartoon_dir, filename)
                print(f"Saved cartoon image to {os.path.join(cartoon_dir, filename)}")


                # save the images after aplying the edit to the path
                black_and_white_image.save(bw_file_path)
                sepia_image.save(sp_file_path)
                cartoon_image.save(ct_file_path)

                # Remove the original image
                # os.remove(image_file_path)

        zip_path = os.path.join(OUTPUT_DIR, f"{session_id}.zip")
        with ZipFile(zip_path, 'w') as ZipF:
            # "for every folder and every file inside session_dir…"
            for root, _, files in os.walk(session_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Example: if file_path="sessions/abc123/images/pic1.png" and session_dir="sessions/abc123", =  "images/pic1.png"
                    rel_file_zip_path = os.path.relpath(file_path, session_dir)
                    ZipF.write(file_path, os.path.join(session_id, rel_file_zip_path))

        response = send_file(zip_path, as_attachment=True, download_name=f"edited_image_{session_id}.zip", mimetype='application/zip')

        def cleanup_session_and_zip():
            shutil.rmtree(session_dir, ignore_errors=True)
            os.remove(zip_path)
        atexit.register(cleanup_session_and_zip)

        return response
    except OSError as e:
        print("cannot create thumbnail for", e)
        return e
    except Exception as e:
        print(f"Error processing upload: {str(e)}")
        return jsonify({"error": f"Failed to process upload: {str(e)}"}), 400


if __name__ == '__main__':
    app.run(debug=True)