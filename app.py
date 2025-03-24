import os
import qrcode
import cloudinary
import cloudinary.uploader
import cloudinary.api
from PIL import Image, ImageDraw, ImageFont
from flask import Flask, request, render_template

# Flask App Setup
app = Flask(__name__)

# Cloudinary Configuration (Replace with your credentials)
cloudinary.config( 
    cloud_name="djr7tven5",
    api_key="683487828554685",
    api_secret="l5EbsR46OgilS0DGj_upJLtORqY"
)

# Configuration
IMAGE_FOLDER = "local_images"  # Folder containing images on your computer
QR_FOLDER = "qr_codes"  # Folder to save QR codes
ACCESS_PIN = "7013"  # Set your PIN here
RENDER_URL = "https://zana-couture-qr.onrender.com"  # Replace with your actual Render URL

# Ensure QR code folder exists
os.makedirs(QR_FOLDER, exist_ok=True)

# Upload images from local folder to Cloudinary and generate QR codes
image_data = {}

for filename in os.listdir(IMAGE_FOLDER):
    if filename.lower().endswith((".png", ".jpg", ".jpeg")):
        local_path = os.path.join(IMAGE_FOLDER, filename)
        
        # Upload image to Cloudinary
        response = cloudinary.uploader.upload(local_path)
        image_url = response["secure_url"]
        image_id = os.path.splitext(filename)[0]  # Remove extension
        image_data[image_id] = {"url": image_url, "password": ACCESS_PIN}
        
        # Generate QR code linking to Render app
        qr_url = f"{RENDER_URL}/view/{image_id}"
        qr = qrcode.make(qr_url)
        
        # Convert QR code to image and add text
        qr = qr.convert("RGB")
        draw = ImageDraw.Draw(qr)
        font = ImageFont.load_default()
        
        # Add text (image name) on top of QR code
        text = image_id
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        image_width, image_height = qr.size
        text_position = ((image_width - text_width) // 2, 10)
        draw.text(text_position, text, fill="black", font=font)
        
        # Save QR code with text
        qr.save(os.path.join(QR_FOLDER, f"{image_id}.png"))

print(f"✅ QR codes generated for {len(image_data)} images!")

# Flask Routes
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/view/<img_id>", methods=["GET", "POST"])
def view_image(img_id):
    if request.method == "POST":
        password = request.form.get("password")
        
        # Validate PIN
        if img_id in image_data and image_data[img_id]["password"] == password:
            return render_template("image.html", image_url=image_data[img_id]["url"])
        else:
            return "Invalid PIN", 403

    return render_template("pin.html", img_id=img_id)

# Start Flask Server
if __name__ == "__main__":  
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port  
    app.run(host="0.0.0.0", port=port)
