AI Social Media Agent

Overview

This project is a powerful, intelligent content generation and strategy tool built using the Streamlit framework and the high-speed Groq API. It's designed for social media managers and marketers to rapidly generate creative ideas, specific captions, and a preliminary posting schedule based on a target topic, platform, and desired tone.

The application leverages Large Language Models (LLMs) to automate the most time-consuming parts of content planning, delivering instant, actionable results via a clean, interactive web interface.

🔗 Submission Deliverables

1. Working Demo Link (Streamlit)
Insert your final live URL from Streamlit Cloud here.*
Working Demo Link: [Insert your deployed Streamlit URL here, e.g., `https://social-media-agent-anushaa07.streamlit.app/`]

2. Git Repository (Public Shared Link)
Public Repository: `https://github.com/Anushaa07/Social-media-agent`
***

Features & Limitations

Core Features
Targeted Content Generation: Users input a Topic, a Platform(e.g., LinkedIn), and a Tone (e.g., Professional) to receive five creative post ideas.
Repurposing Utility: Converts any post idea into platform-specific formats (e.g., Twitter thread, LinkedIn long-form post, YouTube Shorts script).
Content Evaluation:Provides an AI-generated strength Score (0-100), reasons for the score, and specific suggestions for improvement.
Content Scheduling: An interactive scheduler allows users to add generated captions to a simple calendar table for planning.
Rapid Inference: Utilizes the high-speed inference of the Groq API to provide near-instant content drafts.

 Known Limitations

No Live Publishing:The agent generates the schedule data but does not integrate with live social media APIs (like Meta or X) to automatically publish posts.
Session-Based Schedule:The content scheduler data is stored in Streamlit's session state and is **not permanent**. Closing the browser will clear the schedule.

⚙️ Setup & Run Instructions (Local Testing)

Prerequisites

* Python 3.8+
* A valid Groq API Key

1. Clone the Repository

Open your terminal and clone the project:
```bash
git clone [https://github.com/Anushaa07/Social-media-agent.git](https://github.com/Anushaa07/Social-media-agent.git)
cd Social-media-agent
