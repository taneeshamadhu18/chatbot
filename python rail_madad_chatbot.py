import gradio as gr
import torch
from PIL import Image
import numpy as np
from pathlib import Path
import requests

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', source='github') 

complaint_details = {}

def analyze_image_with_yolo(image):
    img = np.array(image)
    results = model(img)
    detected_objects = []
    for obj in results.xyxy[0]:
        if obj[4] > 0.25:
            label = model.names[int(obj[5])]
            detected_objects.append(label)
    if detected_objects:
        response = f"Detected objects: {', '.join(detected_objects)}"
        if "person" in detected_objects:
            return (response + " It looks like a person was detected. Please specify the issue related to the person, such as staff behavior or assistance needed.")
        elif "toilet" in detected_objects:
            return (response + " It seems there is a cleanliness issue. We will notify the cleaning staff to address this.")
        elif "chair" in detected_objects:
            return (response + " If there is an issue with the train's condition, please specify the problem, and we'll escalate it to the maintenance team.")
        else:
            return response + " Please provide more details about your complaint or upload a different image if possible."
    else:
        return "No specific objects detected. Please provide more details about your complaint or upload a different image if possible."

def send_complaint_to_api(complaint_details):
    api_url = "http://example.com/api/complaints"  # Replace w ur API URL
    try:
        response = requests.post(api_url, json=complaint_details)
        if response.status_code == 200:
            return f"Complaint submitted successfully. Response: {response.json()}"
        else:
            return f"Failed to submit complaint. Status Code: {response.status_code}, Response: {response.text}"
    except Exception as e:
        return f"Error submitting complaint: {str(e)}"

def rail_madad_chatbot(user_input, image=None):
    global complaint_details
    if image:
        return analyze_image_with_yolo(image)
    
    user_input_lower = user_input.lower()

    if user_input_lower in ["hi", "hello", "hey"]:
        return "Hello! How can I assist you today?"
    
    if "complaint" in user_input_lower:
        return ("To lodge a complaint, please provide the following details:\n"
                "1. Train Number\n"
                "2. PNR\n"
                "3. Description of the issue\n"
                "You can also upload an image of the issue if available.")

    if "train number" in user_input_lower:
        complaint_details['train_number'] = user_input.split(":")[-1].strip()
        return "Train number recorded. Please provide the PNR."
    elif "pnr" in user_input_lower:
        complaint_details['pnr'] = user_input.split(":")[-1].strip()
        return "PNR recorded. Please describe the issue."
    elif "description" in user_input_lower:
        complaint_details['description'] = user_input.split(":")[-1].strip()

        if all(complaint_details.get(key) for key in ['train_number', 'pnr', 'description']):
            response = send_complaint_to_api(complaint_details)
            return (f"Thank you! Your complaint has been lodged with the following details:\n"
                    f"Train Number: {complaint_details.get('train_number')}\n"
                    f"PNR: {complaint_details.get('pnr')}\n"
                    f"Description: {complaint_details.get('description')}\n"
                    "We will process your complaint and get back to you shortly.\n"
                    + response)
        else:
            return "Description recorded. Please ensure that both Train Number and PNR are provided."

    return "I am here to help you with your complaints. Please describe the issue in detail or upload an image for analysis."

iface = gr.Interface(
    fn=rail_madad_chatbot,
    inputs=[gr.Textbox(label="Your Message"), gr.Image(type="pil", label="Upload an image (optional)")],
    outputs="text",
    title="Rail Madad Chatbot",
    description="Interact with the Rail Madad chatbot. You can ask questions, upload images for analysis, or get updates on your complaints."
)

iface.launch()
