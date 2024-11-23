# NVIDIA_Human_Action_Detection_VLM_Workflow
# 🎥 Action Detection with NVIDIA NEVA

This project compares action detection success rates between synthetic and real videos using NVIDIA's NEVA API. It uses Gradio to provide a user-friendly interface for inputting video files and specifying activities to be analyzed. The project calculates detection rates for each video by processing extracted frames.

---

## 🚀 Features

- Compare success rates for action detection in synthetic vs. real videos.
- Frame extraction and trimming to match video lengths.
- Easy-to-use web interface built with Gradio.
- Supports various video formats: `.mp4`, `.avi`, `.mov`.
- Integrates NVIDIA NEVA API for activity detection.

---

## 🛠️ Installation

1. Clone this repository:
   ```bash
   git https://github.com/VarunKonjeti12/NVIDIA_Human_Action_Detection_VLM_Workflow.git 
   cd NVIDIA_Human_Action_Detection_VLM_Workflow 

## 📝 Usage
1. Upload two videos: one synthetic and one real.
2. Specify the activity you want to detect (e.g., walking, jumping).
3. Click Submit to view the success rates for both videos.

## 📋 Requirements
Python 3.7+
Libraries in requirements.txt:
   * requests
   * gradio
   * moviepy
   * Pillow

## 🛠️ Troubleshooting
Issue: Video not processing
   * Ensure the video format is supported (.mp4, .avi, .mov).
   * Verify the video is not corrupt.
Issue: NEVA API errors
   * Check your API token and endpoint validity.

## 🌟 Acknowledgments
* NVIDIA NEVA API for powering activity detection.
* Gradio for the intuitive interface.

## My API Key:
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
