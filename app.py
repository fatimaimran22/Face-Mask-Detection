from flask import Flask, render_template, request, jsonify
import os
from PIL import Image
import numpy as np
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def analyze_image(image_path):
    """
    A simple function to analyze if a person is wearing a mask
    This is a placeholder function - you can replace it with your own logic
    """
    try:
        # Open and convert image to grayscale
        img = Image.open(image_path).convert('L')
        img = img.resize((224, 224))
        
        # Convert to numpy array and normalize
        img_array = np.array(img) / 255.0
        
        # Example simple analysis (this is a placeholder)
        # You can replace this with your own mask detection logic
        # For now, this just checks if the image is generally darker in the mask region
        
        # Assume the mask region is in the middle third of the face
        height, width = img_array.shape
        mask_region = img_array[height//3:2*height//3, width//3:2*width//3]
        
        # Calculate average brightness in mask region
        mask_brightness = np.mean(mask_region)
        
        # If the mask region is darker (lower brightness), assume mask is present
        # This is a very simple heuristic and should be replaced with your actual logic
        is_wearing_mask = mask_brightness < 0.5
        confidence = abs(0.5 - mask_brightness) * 2  # Simple confidence calculation
        
        return is_wearing_mask, min(confidence * 100, 100)
    except Exception as e:
        raise Exception(f"Error analyzing image: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        # Save the file temporarily
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)
        
        try:
            # Analyze the image
            is_wearing_mask, confidence = analyze_image(file_path)
            result = "Wearing Mask" if is_wearing_mask else "Not Wearing Mask"
            
            return jsonify({
                'result': result,
                'confidence': f"{confidence:.2f}%",
                'image_path': file.filename
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        
    return jsonify({'error': 'Error processing file'}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
