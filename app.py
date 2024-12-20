import requests
import base64
from moviepy.video.io.VideoFileClip import VideoFileClip
from PIL import Image
from io import BytesIO
import gradio as gr

# NVIDIA NEVA API setup
API_ENDPOINT = "https://ai.api.nvidia.com/v1/vlm/nvidia/neva-22b"
AUTH_TOKEN = "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"  # Use securely for production

def capture_frames(video_file, total_frames=16):
    """Capture equally spaced frames from the provided video."""
    try:
        video = VideoFileClip(video_file)
        video_length = video.duration

        if video_length == 0:
            raise ValueError("The video has a duration of zero seconds. Check the file.")

        # Extracting frames at evenly spaced intervals
        extracted_frames = [
            video.get_frame(i * video_length / total_frames) for i in range(total_frames)
        ]
        return [Image.fromarray(frame_data) for frame_data in extracted_frames]

    except Exception as err:
        print(f"Error in capture_frames: {err}")
        return []

def convert_image_to_base64(image):
    """Convert an image to a Base64-encoded string."""
    try:
        buffer = BytesIO()
        image.save(buffer, format="PNG")  # Using PNG format as required
        encoded_data = base64.b64encode(buffer.getvalue()).decode()
        return encoded_data
    except Exception as err:
        print(f"Error in convert_image_to_base64: {err}")
        return ""

def query_neva_api(image_base64, activity):
    """Send a request to NVIDIA NEVA API to detect the specified activity in the image."""
    if not image_base64:
        print("Image data is missing, skipping API call.")
        return False

    headers = {
        "Authorization": f"Bearer {AUTH_TOKEN}",
        "Accept": "application/json",
    }
    payload = {
        "messages": [
            {
                "role": "user",
                "content": f'Do you observe the action "{activity}" in this image? <img src="data:image/png;base64,{image_base64}" />',
            }
        ],
        "max_tokens": 512,  # Reduced token count for efficiency
        "temperature": 0.7,  # Adjusted temperature for more consistent responses
        "top_p": 1.0,        # Increased top_p for better result coverage
        "stream": False,
    }

    try:
        response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=30)  # Added timeout

        if response.status_code == 200:
            response_data = response.json()
            if 'choices' in response_data and response_data['choices']:
                response_content = response_data['choices'][0].get('message', {}).get('content', "")
                return "yes" in response_content.lower()
            else:
                print("No valid choices returned in the response.")
        else:
            print(f"API call failed with status code: {response.status_code}")

    except requests.exceptions.Timeout:
        print("The request timed out.")
    except Exception as err:
        print(f"Error in query_neva_api: {err}")
    return False

def compute_detection_rate(images, activity):
    """Calculating the percentage of frames where the activity is detected."""
    try:
        positive_detections = 0

        for image in images:
            image_b64 = convert_image_to_base64(image)
            if query_neva_api(image_b64, activity):
                positive_detections += 1

        return (positive_detections / len(images)) * 100 if images else 0

    except ZeroDivisionError:
        print("No frames available for detection rate calculation.")
        return 0

def trim_videos(video1_path, video2_path, trim_length=None):
    """Trim two videos to the same duration based on user-provided or shorter video duration."""
    try:
        clip1 = VideoFileClip(video1_path)
        clip2 = VideoFileClip(video2_path)
        min_duration = min(clip1.duration, clip2.duration)

        # Check if the user-provided trim length is valid
        if trim_length is not None:
            if trim_length <= 0:
                return "Error: Trim length must be greater than 0 seconds.", None, None
            trim_duration = min(trim_length, min_duration)
        else:
            trim_duration = min_duration

        return None, clip1.subclip(0, trim_duration), clip2.subclip(0, trim_duration)
    except Exception as err:
        print(f"Error in trim_videos: {err}")
        return "Error: Failed to trim videos. Please check your inputs.", None, None

def analyze_videos(video_a_path, video_b_path, activity, trim_length):
    """Analyze two videos for the specified activity and return success rates."""
    trim_result, trimmed_a, trimmed_b = trim_videos(video_a_path, video_b_path, trim_length)
    if isinstance(trim_result, str):  # This means an error occurred
        return trim_result, None

    frames_a = capture_frames(trimmed_a.filename)
    frames_b = capture_frames(trimmed_b.filename)

    if not frames_a or not frames_b:
        return "Error: Failed to extract frames from one or both videos.", None

    success_rate_a = compute_detection_rate(frames_a, activity)
    success_rate_b = compute_detection_rate(frames_b, activity)

    return (
        f"Video A '{activity}' Success Rate: {success_rate_a:.2f}%",
        f"Video B '{activity}' Success Rate: {success_rate_b:.2f}%",
    )

# Gradio interface for action detection comparison
ui = gr.Interface(
    fn=analyze_videos,
    inputs=[
        gr.File(label="Synthetic Video (Input A)", file_types=[".mp4", ".avi", ".mov"]),
        gr.File(label="Real Video (Input B)", file_types=[".mp4", ".avi", ".mov"]),
        gr.Textbox(label="Specify the Activity (e.g., walking, jumping)"),
        gr.Number(label="Trim Length (seconds, optional)", value=None),
    ],
    outputs=[
        gr.Textbox(label="Analysis for Synthetic Video"),
        gr.Textbox(label="Analysis for Real Video"),
    ],
    title="Action Detection via NVIDIA NEVA",
    description="Compare action detection success rates between a synthetic and a real video. Optionally, specify a trim length.",
)

if __name__ == "__main__":
    ui.launch(share = True)
