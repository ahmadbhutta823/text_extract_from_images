import os
import base64
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def encode_image_to_base64(image_path):
    """
    Convert image to base64 string
    """
    with Image.open(image_path) as img:
        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Resize if image is too large (max 8192x8192)
        max_size = 8192
        if img.size[0] > max_size or img.size[1] > max_size:
            img.thumbnail((max_size, max_size))
        
        # Save to bytes
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

def extract_text_from_image(image_path):
    """
    Extract text from image using GPT-4 Vision
    """
    try:
        # Encode image
        base64_image = encode_image_to_base64(image_path)
        
        # Create message for GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": ("You are an OCR extraction engine. Your task is to extract data from an autoclave image report. DIGIT ORDER AND ACCURACY ARE CRITICAL.\n\n"
                                   "⚠️ CRITICAL: READ EACH DIGIT FROM LEFT TO RIGHT. DO NOT REARRANGE DIGITS.\n"
                                   "Example: If you see '247', it must not become '274'. Each digit must stay in its exact position.\n\n"
                                   "READ AND EXTRACT EACH LINE INDIVIDUALLY. Follow these rules STRICTLY:\n\n"
                                   "1. Extract and write **each entry exactly** as it appears in the image.\n"
                                   "2. For every line in the format `[ID] [Temperature]°F [Pressure]`:\n"
                                   "   - READ **every digit** in the temperature and pressure carefully.\n"
                                   "   - Ensure °F is included.\n"
                                   "   - Do not skip lines. Even if a value is 000°F 00P, include it.\n"
                                   "3. Characters that can look similar (1, 7 / 3, 8 / 5, 6 / 0, 8) must be double-checked.\n"
                                   "4. Do NOT reformat, interpret, infer, or skip **any values**.\n"
                                   "5. Return the result **as-is** from the image. Preserve order.\n\n"
                                   "💡 Format:\n"
                                   "[ID] [Temp]°F [Pressure]\n\n"
                                   "✅ EXACT Examples - Check digit order carefully:\n"
                                   "H17 247°F 16P  (must be 247, NOT 274)\n"
                                   "H13 223°F 08P  (must be 223, NOT 232 or 273)\n"
                                   "H05 142°F 00P\n\n"
                                   "⚠️ CRITICAL TIME AND DRY FORMAT:\n"
                                   "These are two separate fields that must not be mixed up:\n"
                                   "DRY  :01MIN    (Dry time - exactly as shown)\n"
                                   "TIME :10MIN    (Time - exactly as shown)\n\n"
                                   "Other fields to extract EXACTLY if present:\n"
                                   "- AUTOCALVE NO\n"
                                   "- LOAD NO\n"
                                   "- OPERATOR\n"
                                   "- TEMP\n"
                                   "- PROG\n"
                                   "- DATE\n"
                                   "- Version\n\n"
                                   "⚠️ READ CAREFULLY:\n"
                                   "- DRY and TIME are different fields\n"
                                   "- Keep exact spacing and colons\n"
                                   "- Do not swap or combine these values\n"
                                   "- Extract each line independently\n\n"
                                   "ONLY RETURN RAW TEXT FROM IMAGE.\n"
                                   "DO NOT WRITE AN EXPLANATION, JUST RETURN RAW TEXT.")
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=4096
        )
        
        # Extract the response text
        extracted_text = response.choices[0].message.content
        return extracted_text.strip()
    
    except Exception as e:
        return f"Error processing {image_path}: {str(e)}"

def check_environment():
    """
    Check if the environment is properly set up
    """
    if not os.getenv('OPENAI_API_KEY'):
        raise ValueError("OPENAI_API_KEY not found in environment variables. Please check your .env file.")
    
    # Test OpenAI client
    try:
        client.models.list()
        print("✓ Successfully connected to OpenAI API")
    except Exception as e:
        raise Exception(f"Failed to connect to OpenAI API: {str(e)}")

def main():
    try:
        # Check environment setup
        check_environment()
        
        # Create output directory if it doesn't exist
        output_dir = "extracted_text"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Get all image files from the images directory
        images_dir = "images"
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif']
        
        image_files = []
        for file in os.listdir(images_dir):
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(images_dir, file))
        
        if not image_files:
            print("No image files found in the images directory.")
            return
    
        # Sort files for consistent output
        image_files.sort()
        
        # Create output file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = os.path.join(output_dir, f"extracted_text_{timestamp}.txt")
        
        print(f"Processing {len(image_files)} images...")
        print(f"Output will be saved to: {output_file}")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("TEXT EXTRACTION FROM AUTOCLAVE IMAGES (GPT-4 Vision)\n")
            f.write("=" * 80 + "\n")
            f.write(f"Extraction Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Images Processed: {len(image_files)}\n")
            f.write("=" * 80 + "\n\n")
            
            for i, image_path in enumerate(image_files, 1):
                print(f"Processing {i}/{len(image_files)}: {os.path.basename(image_path)}")
                
                # Extract text from image
                extracted_text = extract_text_from_image(image_path)
                
                # Write to file
                f.write(f"IMAGE {i}: {os.path.basename(image_path)}\n")
                f.write("-" * 60 + "\n")
                f.write(extracted_text)
                f.write("\n\n" + "=" * 80 + "\n\n")
        
        print(f"\nText extraction completed!")
        print(f"Results saved to: {output_file}")
        
        # Create a summary file
        summary_file = os.path.join(output_dir, f"summary_{timestamp}.txt")
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("EXTRACTION SUMMARY\n")
            f.write("=" * 50 + "\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Images processed: {len(image_files)}\n\n")
            
            for i, image_path in enumerate(image_files, 1):
                extracted_text = extract_text_from_image(image_path)
                word_count = len(extracted_text.split())
                char_count = len(extracted_text)
                
                f.write(f"{i}. {os.path.basename(image_path)}\n")
                f.write(f"   Words: {word_count}, Characters: {char_count}\n")
                f.write(f"   Preview: {extracted_text[:100]}...\n\n")
        
        print(f"Summary saved to: {summary_file}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()