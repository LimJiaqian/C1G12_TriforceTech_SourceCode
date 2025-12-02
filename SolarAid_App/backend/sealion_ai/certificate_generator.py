"""
Certificate Generator using SEA-LION AI
Generates Sadaqah Jariah certificates with AI-generated poetic captions
"""

import os
import requests
from dotenv import load_dotenv
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import base64

load_dotenv()
API_KEY = os.getenv("SEA_LION_API_KEY2")
URL = "https://api.sea-lion.ai/v1/completions"

def generate_certificate_caption(kwh, impact_metric, context, co2_kg):
    """
    Generate a poetic caption for the certificate using SEA-LION AI
    
    Args:
        kwh (float): kWh donated
        impact_metric (str): The specific impact story (e.g., "120 hours of vaccine refrigeration")
        context (str): The recipient context (e.g., "a rural clinic")
        co2_kg (float): CO2 saved in kg
        
    Returns:
        str: AI-generated caption or fallback message
    """
    
    if not API_KEY:
        return "Your gift of light brings hope and power to those who need it most."
    
    system_prompt = """You are a warm, humble Malaysian volunteer. 
Write a 1-sentence poetic caption for a 'Sadaqah Jariah' certificate. 
Tone: Syukur (Grateful), Humble, Hopeful.
Use Manglish or Standard English with Malaysian warmth.
Do NOT mention money. Do NOT mention Zakat. 
Focus on the 'Cahaya' (Light) and 'Bantuan' (Help) given.

CRITICAL: Do NOT provide a list. Do NOT say 'Here is an option' or 'Here are a few options'. 
Output ONLY the single caption text itself, nothing else. Just one beautiful sentence."""
    
    user_prompt = f"""
Donation Impact: {kwh} kWh.
Result: {impact_metric} at {context}.
CO2 Saved: {co2_kg} kg.

Write a caption celebrating this contribution to the community."""
    
    payload = {
        "model": "aisingapore/Gemma-SEA-LION-v4-27B-IT",
        "prompt": system_prompt + "\n\n" + user_prompt,
        "temperature": 0.9,
        "max_tokens": 100
    }
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=15)
        data = response.json()
        
        if "choices" in data and len(data["choices"]) > 0:
            text = data["choices"][0]["text"].strip()
            
            # Clean up the text - remove unwanted prefixes
            text = text.strip('"').strip()
            
            # Remove common AI response patterns
            unwanted_patterns = [
                "Here is an option:",
                "Here are a few options:",
                "Here's a caption:",
                "Option 1:",
                "1.",
                "2.",
                "3.",
            ]
            
            for pattern in unwanted_patterns:
                if text.startswith(pattern):
                    text = text[len(pattern):].strip()
            
            # Remove any leading numbers or bullets
            import re
            text = re.sub(r'^\d+\.\s*', '', text)
            text = text.strip('"').strip()
            
            if text:
                return text
        
        # Fallback if AI returns empty
        return "Your generous gift brings cahaya and harapan to our community. Terima kasih!"
        
    except Exception as e:
        print(f"SEA-LION API Error: {e}")
        return "Your gift of light brings hope and power to those who need it most."


def create_certificate_image(kwh, impact_metric, co2_kg, ai_text):
    """
    Create a certificate image with the provided data
    
    Args:
        kwh (float): kWh donated
        impact_metric (str): Human impact metric with units
        co2_kg (float): CO2 saved in kg
        ai_text (str): AI-generated caption
        
    Returns:
        BytesIO: Image buffer containing the certificate
    """
    
    # Certificate dimensions (portrait)
    width, height = 1080, 1920
    
    # Create image with dark background
    img = Image.new('RGB', (width, height), color='#0F172A')  # slate-900
    draw = ImageDraw.Draw(img)
    
    # Try to load fonts (fallback to default if not available)
    try:
        font_header = ImageFont.truetype("arial.ttf", 60)
        font_hero = ImageFont.truetype("arialbd.ttf", 220)
        font_unit = ImageFont.truetype("arial.ttf", 70)
        font_impact_num = ImageFont.truetype("arialbd.ttf", 90)
        font_impact_text = ImageFont.truetype("arial.ttf", 45)
        font_co2 = ImageFont.truetype("arial.ttf", 50)
        font_caption = ImageFont.truetype("ariali.ttf", 55)
        font_footer = ImageFont.truetype("arial.ttf", 35)
    except:
        # Fallback to default font
        font_header = ImageFont.load_default()
        font_hero = ImageFont.load_default()
        font_unit = ImageFont.load_default()
        font_impact_num = ImageFont.load_default()
        font_impact_text = ImageFont.load_default()
        font_co2 = ImageFont.load_default()
        font_caption = ImageFont.load_default()
        font_footer = ImageFont.load_default()
    
    # 1. Header - "JARIAH CERTIFICATE"
    header_text = "JARIAH CERTIFICATE"
    header_bbox = draw.textbbox((0, 0), header_text, font=font_header)
    header_width = header_bbox[2] - header_bbox[0]
    draw.text(((width - header_width) / 2, 200), header_text, fill='#10B981', font=font_header)  # emerald-400
    
    # 2. Hero Metric - kWh
    kwh_text = str(int(kwh))
    kwh_bbox = draw.textbbox((0, 0), kwh_text, font=font_hero)
    kwh_width = kwh_bbox[2] - kwh_bbox[0]
    draw.text(((width - kwh_width) / 2, 350), kwh_text, fill='#FFFFFF', font=font_hero)
    
    # kWh label
    kwh_label = "kWh Generated"
    kwh_label_bbox = draw.textbbox((0, 0), kwh_label, font=font_unit)
    kwh_label_width = kwh_label_bbox[2] - kwh_label_bbox[0]
    draw.text(((width - kwh_label_width) / 2, 600), kwh_label, fill='#9CA3AF', font=font_unit)  # gray-400
    
    # 3. Impact Box (with border)
    box_y = 750
    box_height = 300
    box_padding = 40
    draw.rounded_rectangle(
        [(box_padding, box_y), (width - box_padding, box_y + box_height)],
        radius=30,
        outline='#10B981',  # emerald-500
        width=3,
        fill='#064E3B'  # emerald-900/50
    )
    
    # Extract number and text from impact_metric
    metric_parts = impact_metric.split(' ', 1)
    metric_number = metric_parts[0]
    metric_text = metric_parts[1] if len(metric_parts) > 1 else ""
    
    # Impact number
    impact_num_bbox = draw.textbbox((0, 0), metric_number, font=font_impact_num)
    impact_num_width = impact_num_bbox[2] - impact_num_bbox[0]
    draw.text(((width - impact_num_width) / 2, box_y + 60), metric_number, fill='#6EE7B7', font=font_impact_num)  # emerald-300
    
    # Impact text (word wrap)
    impact_text_lines = []
    words = metric_text.upper().split()
    current_line = ""
    for word in words:
        test_line = current_line + " " + word if current_line else word
        test_bbox = draw.textbbox((0, 0), test_line, font=font_impact_text)
        if test_bbox[2] - test_bbox[0] < (width - 2 * box_padding - 80):
            current_line = test_line
        else:
            if current_line:
                impact_text_lines.append(current_line)
            current_line = word
    if current_line:
        impact_text_lines.append(current_line)
    
    text_y = box_y + 180
    for line in impact_text_lines:
        line_bbox = draw.textbbox((0, 0), line, font=font_impact_text)
        line_width = line_bbox[2] - line_bbox[0]
        draw.text(((width - line_width) / 2, text_y), line, fill='#D1FAE5', font=font_impact_text)  # emerald-100
        text_y += 60
    
    # 4. CO2 Environmental Stat
    co2_text = f"🌱 {co2_kg} kg CO2 Avoided"
    co2_bbox = draw.textbbox((0, 0), co2_text, font=font_co2)
    co2_width = co2_bbox[2] - co2_bbox[0]
    draw.text(((width - co2_width) / 2, 1150), co2_text, fill='#9CA3AF', font=font_co2)
    
    # 5. AI-Generated Caption (word wrap)
    caption_lines = []
    words = ai_text.split()
    current_line = ""
    max_caption_width = width - 160
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        test_bbox = draw.textbbox((0, 0), test_line, font=font_caption)
        if test_bbox[2] - test_bbox[0] < max_caption_width:
            current_line = test_line
        else:
            if current_line:
                caption_lines.append(current_line)
            current_line = word
    if current_line:
        caption_lines.append(current_line)
    
    caption_y = 1280
    for line in caption_lines:
        line_bbox = draw.textbbox((0, 0), f'"{line}"', font=font_caption)
        line_width = line_bbox[2] - line_bbox[0]
        draw.text(((width - line_width) / 2, caption_y), f'"{line}"', fill='#D1D5DB', font=font_caption)  # gray-300
        caption_y += 70
    
    # 6. Footer
    footer_text = "VERIFIED BY HYCO PLATFORM"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    footer_width = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_width) / 2, 1780), footer_text, fill='#6B7280', font=font_footer)  # gray-500
    
    # Convert to bytes
    img_buffer = BytesIO()
    img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    
    return img_buffer


def generate_certificate(kwh, recipient_type='home'):
    """
    Main function to generate certificate with all metrics
    
    Args:
        kwh (float): kWh donated
        recipient_type (str): Type of recipient ('clinic', 'school', 'disaster', 'home')
        
    Returns:
        dict: Contains base64 image and metrics
    """
    from ..utils.impactCalculator import calculate_impact
    
    # Calculate impact
    impact = calculate_impact(kwh)
    
    # Select specific story based on recipient type
    specific_stat = ""
    context = ""
    
    if recipient_type == 'clinic':
        specific_stat = f"{impact['stories']['clinic']['val']} {impact['stories']['clinic']['unit']}"
        context = "a rural clinic"
    elif recipient_type == 'disaster':
        specific_stat = f"{impact['stories']['disaster']['val']} {impact['stories']['disaster']['unit']}"
        context = "a flood relief center"
    elif recipient_type == 'school':
        specific_stat = f"{impact['stories']['school']['val']} {impact['stories']['school']['unit']}"
        context = "a night revision class"
    else:  # 'home'
        specific_stat = f"{impact['stories']['home']['val']} {impact['stories']['home']['unit']}"
        context = "a family home"
    
    # Generate AI caption
    ai_text = generate_certificate_caption(kwh, specific_stat, context, impact['co2_kg'])
    
    # Create certificate image
    img_buffer = create_certificate_image(kwh, specific_stat, impact['co2_kg'], ai_text)
    
    # Convert to base64 for web display
    img_base64 = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    
    return {
        "image_base64": f"data:image/png;base64,{img_base64}",
        "impact_metric": specific_stat,
        "co2_kg": impact['co2_kg'],
        "ai_text": ai_text
    }
