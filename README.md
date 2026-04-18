# Graduation-Project-Privacy-System
🎥 Privacy-Aware People Tracking System

📌 Overview

A full-stack intelligent surveillance system that detects, tracks, and anonymizes individuals in real-time video streams while securing stored data.

The system integrates computer vision and cybersecurity principles to provide a privacy-focused monitoring solution suitable for real-world environments such as universities, offices, and public spaces.

⸻

🎯 Objectives
	•	Detect and track individuals in real-time video streams
	•	Protect identities through face anonymization
	•	Secure sensitive data using encryption
	•	Build a complete end-to-end monitoring system

⸻

⚙️ Core Features
	•	🎥 Real-time video capture (live camera & uploaded video)
	•	👤 Human detection using YOLOv8
	•	🔄 Multi-object tracking using DeepSORT
	•	😶 Face anonymization (blur/pixelation)
	•	🔐 Data encryption before storage
	•	📊 Interactive dashboard (counts, alerts, monitoring)

⸻

🧠 How It Works
	1.	Video is captured from a live camera or uploaded source
	2.	YOLOv8 detects individuals in each frame
	3.	DeepSORT assigns unique IDs and tracks movement across frames
	4.	Faces are anonymized using blur/pixelation
	5.	Processed data is encrypted and stored securely
	6.	Results are visualized through a dashboard

⸻

🧱 System Architecture
	•	Frontend: Web interface (TypeScript / HTML / CSS)
	•	Backend: Python-based processing
	•	Computer Vision: YOLOv8 + DeepSORT
	•	Encryption: Python Cryptography library
	•	Deployment (concept): Cloud-ready (AWS EC2)

⸻

🔐 Security & Privacy Design

This system was designed with a strong focus on protecting sensitive visual data:
	•	Faces are anonymized before storage
	•	All stored data is encrypted to prevent unauthorized access
	•	Data is validated before being saved
	•	Access to stored data is restricted to authorized users only

⚠️ Security Considerations
	•	Preventing exposure of personal identities
	•	Reducing risks of surveillance misuse
	•	Ensuring secure data handling across the pipeline

⸻

🛠️ Technologies Used
	•	Python
	•	OpenCV
	•	YOLOv8
	•	DeepSORT
	•	Cryptography Library
	•	TypeScript
	•	HTML / CSS

⸻

📊 Results
	•	Successfully detected and tracked multiple individuals in real-time
	•	Applied anonymization without significantly affecting detection accuracy
	•	Ensured secure storage of processed data
	•	Built a working dashboard for monitoring and alerts

  📂 Project Structure

  backend/
  frontend/
  data/
yolov8n.pt
requirements.txt

▶️ How to Run
	1.	Install dependencies:
       pip install -r requirements.txt

  2.	Run backend:
       python main.py

3.	Start frontend:

	•	Open the interface in your browser or run the frontend environment

📸 Demo
<img width="1236" height="450" alt="preliminary-image" src="https://github.com/user-attachments/assets/d23c56c1-fb63-4a5f-92e5-4d82252bd012" />


⸻

🧠 Security Insight

This project demonstrates how surveillance systems can be redesigned to prioritize privacy and security, ensuring that sensitive data is protected throughout the entire processing pipeline — not just at storage.

⸻

🚀 Future Improvements
	•	Multi-camera support
	•	Advanced behavior analysis
	•	Improved encryption mechanisms
	•	Full cloud deployment

⸻

📌 Note

This project reflects a combination of system development and defensive security thinking, aligning with real-world cybersecurity practices and privacy-by-design principles.
