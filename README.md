# Wazuh SIEM & LLM Integration for Advanced Threat Detection

## 📌 Overview 
This project integrates Wazuh SIEM with a Large Language Model (Gemini) to automate alert triage, reduce false positives, and send real-time notifications via Telegram.

## 🚀 Key Features 
*   **Custom Threat Detection:** Developed custom Wazuh rules to detect Nmap port scanning and Hydra SSH brute-force attacks.
*   **Asynchronous Processing:** Built a Python integration script with a 30-second buffer window to batch logs and prevent API rate-limiting.
*   **AI-Driven Triage:** Utilized Prompt Engineering to analyze log context, differentiate between human errors and actual attacks, and generate actionable reports.
*   **Real-time Alerting:** Automated push notifications to Telegram with specific firewall blocking recommendations.

## 🛠️ Tech Stack 
*   **SIEM:** Wazuh, Linux System Logs (auth.log, syslog)
*   **Scripting:** Python
*   **AI/LLM:** Google Gemini API
*   **Tools:** Nmap, Hydra, Telegram Bot API

## 📸 Results
<img width="634" height="527" alt="image" src="https://github.com/user-attachments/assets/5e7b3769-4736-45a1-8a18-cd95291893e8" />
<img width="646" height="724" alt="image" src="https://github.com/user-attachments/assets/9bc84d7e-9239-47a1-9578-adf81f450640" />
<img width="639" height="863" alt="image" src="https://github.com/user-attachments/assets/4035c65a-72be-4d21-a3c8-073fe5a55958" />
<img width="615" height="990" alt="image" src="https://github.com/user-attachments/assets/39a0416f-d2ce-4eef-a1a5-3c1ba5f515bb" />
<img width="438" height="332" alt="image" src="https://github.com/user-attachments/assets/f6451bb8-59c0-485d-a0a0-ecd9c133cc93" />
<img width="434" height="312" alt="image" src="https://github.com/user-attachments/assets/235d848f-7a1d-4f4e-9066-53e11cd0fd84" />
<img width="434" height="347" alt="image" src="https://github.com/user-attachments/assets/48122e39-5a32-45b0-80ff-28ef6db97e7a" />
<img width="441" height="204" alt="image" src="https://github.com/user-attachments/assets/820a3736-4509-4a54-8aae-1089968cb56e" />

