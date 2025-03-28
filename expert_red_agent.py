import streamlit as st
import requests
import google.generativeai as genai
from openai import OpenAI, AzureOpenAI
from anthropic import Anthropic
from mistralai import Mistral
from groq import Groq

# --------- Expert RED Compliance Agent --------- #

# Function to get expert analysis from the selected LLM provider
def get_expert_analysis(prompt):
    provider = st.session_state.get("model_provider", "OpenAI API")
    expert_analysis = ""
    # Check the selected provider and call the appropriate API
    # Note: Replace the placeholders with your actual API keys and model names
    # Note: You can also use environment variables to store sensitive information
    if provider == "OpenAI API":
        openai_api_key = st.session_state.get("openai_api_key", "")
        selected_model = st.session_state.get("selected_model", "gpt-4o")
        client = OpenAI(api_key=openai_api_key)
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": "You are a cybersecurity and EU regulatory compliance expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000
        )
        expert_analysis = response.choices[0].message.content

    elif provider == "Anthropic API":
        anthropic_api_key = st.session_state.get("anthropic_api_key", "")
        anthropic_model = st.session_state.get("selected_model", "claude-3-5-sonnet-latest")
        client = Anthropic(api_key=anthropic_api_key)
        response = client.messages.create(
            model=anthropic_model,
            max_tokens=3000,
            system="You are a cybersecurity and EU regulatory compliance expert.",
            messages=[{"role": "user", "content": prompt}]
        )
        expert_analysis = "".join(block.text for block in response.content)

    elif provider == "Azure OpenAI Service":
        azure_api_endpoint = st.session_state.get("azure_api_endpoint", "")
        azure_api_key = st.session_state.get("azure_api_key", "")
        azure_deployment_name = st.session_state.get("azure_deployment_name", "")
        azure_api_version = st.session_state.get("azure_api_version", "2023-12-01-preview")
        client = AzureOpenAI(
            azure_endpoint=azure_api_endpoint,
            api_key=azure_api_key,
            api_version=azure_api_version
        )
        response = client.chat.completions.create(
            model=azure_deployment_name,
            messages=[
                {"role": "system", "content": "You are a cybersecurity and EU regulatory compliance expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000
        )
        expert_analysis = response.choices[0].message.content

    elif provider == "Google AI API":
        google_api_key = st.session_state.get("google_api_key", "")
        google_model = st.session_state.get("selected_model", "gemini-2.0-flash")
        genai.configure(api_key=google_api_key)
        model = genai.GenerativeModel(google_model)
        response = model.generate_content(prompt)
        expert_analysis = response.candidates[0].content.parts[0].text

    elif provider == "Mistral API":
        mistral_api_key = st.session_state.get("mistral_api_key", "")
        mistral_model = st.session_state.get("selected_model", "mistral-large-latest")
        client = Mistral(api_key=mistral_api_key)
        response = client.chat.complete(
            model=mistral_model,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "text"}
        )
        expert_analysis = response.choices[0].message.content

    elif provider == "Ollama":
        ollama_endpoint = st.session_state.get("ollama_endpoint", "http://localhost:11434")
        selected_model = st.session_state.get("selected_model", "local-model")
        url = ollama_endpoint.rstrip("/") + "/api/chat"
        data = {
            "model": selected_model,
            "stream": False,
            "messages": [
                {"role": "system", "content": "You are a cybersecurity and EU regulatory compliance expert."},
                {"role": "user", "content": prompt}
            ]
        }
        response = requests.post(url, json=data, timeout=60)
        response.raise_for_status()
        expert_analysis = response.json()["message"]["content"]

    elif provider == "LM Studio Server":
        lm_studio_endpoint = st.session_state.get("lm_studio_endpoint", "http://localhost:1234")
        selected_model = st.session_state.get("selected_model", "local-model")
        client = OpenAI(
            base_url=f"{lm_studio_endpoint}/v1",
            api_key="not-needed"
        )
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": "You are a cybersecurity and EU regulatory compliance expert."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=3000
        )
        expert_analysis = response.choices[0].message.content

    elif provider == "Groq API":
        groq_api_key = st.session_state.get("groq_api_key", "")
        groq_model = st.session_state.get("selected_model", "")
        client = Groq(api_key=groq_api_key)
        response = client.chat.completions.create(
            model=groq_model,
            messages=[
                {"role": "system", "content": "You are a cybersecurity and EU regulatory compliance expert."},
                {"role": "user", "content": prompt}
            ]
        )
        expert_analysis = response.choices[0].message.content

    else:
        expert_analysis = "No valid LLM provider selected."
    
    return expert_analysis

# Function to run the expert agent for RED compliance evaluation
def run_expert_agent():
    def extract_relevant_threats(threat_type):
        """ Extracts threats related to a specific category by checking the threat model content. """
        threat_model = st.session_state.get("threat_model", [])

        # Convert to string if it's a dictionary-based list
        if isinstance(threat_model, list):
            threat_entries = []
            for item in threat_model:
                if isinstance(item, dict):
                    threat_entries.append(item.get("description", ""))  # Extract "description" field if available
                elif isinstance(item, str):
                    threat_entries.append(item)
            
            threat_text = " ".join(threat_entries).lower()
        else:
            threat_text = str(threat_model).lower()

        return threat_text if threat_type in threat_text else "No relevant issues found"

    def extract_relevant_mitigations(mitigation_type):
        """ Extracts mitigations related to a specific category by checking the mitigations content. """
        mitigations = st.session_state.get("mitigations", [])

        # Convert to string if it's a dictionary-based list
        if isinstance(mitigations, list):
            mitigation_entries = []
            for item in mitigations:
                if isinstance(item, dict):
                    mitigation_entries.append(item.get("description", ""))  # Extract "description" field if available
                elif isinstance(item, str):
                    mitigation_entries.append(item)
            
            mitigation_text = " ".join(mitigation_entries).lower()
        else:
            mitigation_text = str(mitigations).lower()

        return mitigation_text if mitigation_type in mitigation_text else "N/A"

    prompt = f"""
You are a **cybersecurity and EU regulatory compliance expert**, specializing in **Radio Equipment Directive (RED, Directive 2014/53/EU)** and its harmonized standards **18031-1, 18031-2, and 18031-3**.

Your task is to evaluate a **specific product under evaluation (ToE)** using the **available security analysis inputs**:

- **Threat Model:**  
  {st.session_state.get("threat_model", "Not available")}

- **Attack Tree:**  
  {st.session_state.get("attack_tree", "Not available")}

- **Mitigations:**  
  {st.session_state.get("mitigations", "Not available")}

- **DREAD Assessment:**  
  {st.session_state.get("dread_assessment", "Not available")}

- **Test Cases:**  
  {st.session_state.get("test_cases", "Not available")}

---

### **🚨 Strict Scope Control**
- **DO NOT create new threats or risks** beyond what is explicitly stated in the Threat Model and Attack Tree.
- **DO NOT assume mitigations exist** unless they are explicitly listed in the Mitigations section.
- **ONLY evaluate compliance issues that directly map to the available security assessment inputs.**
- **If no threat is mentioned for a specific RED requirement, state that no compliance gaps were identified in that area.**

---

## **1. Overall Compliance Summary**
- Remind the reader of the **product under evaluation (ToE)** and the **scope of the security assessment**.
- Provide a **summary of the identified security threats** based strictly on the provided inputs.
- Identify **any RED compliance gaps** that are explicitly mentioned in the security assessment.
- If no threats are identified in the available inputs, state:  
  **"No explicit security threats were identified in the provided assessment. However, further evaluation may be needed to confirm compliance with RED security requirements."**

---

## **2. Compliance Analysis Based on Security Inputs**
We will assess compliance based on three main categories:  

### **📌 Category 1: Network Connected Equipment (18031-1)**  
#### **Key Compliance Areas**
- **Software Safety**: Protection against unauthorized control, firmware alterations.  
- **Communication Security**: Encryption for data interception protection.  
- **Data Protection**: Ensuring confidentiality, integrity, and availability.  
- **Compromise Prevention**: Preventing breaches and unauthorized actions.  
- **Remote Control Risks (IoT, 5G, etc.)**: Securing remote device access.  
- **Security Measures**: Implementing firewalls, intrusion detection.  
- **Authentication**: Strong authentication for users and devices.  
- **Physical Attacks**: Protecting against hardware tampering.  
- **Smart Sensors**: Ensuring secure data collection and preventing manipulation.  
- **Remote Management**: Secure administration of connected devices.  

#### **Assessment Table**
| **Requirement**                      | **Identified Issues (Before Mitigations)** | **Confirmed Mitigations (If Provided)** | **Compliance Status** |
|--------------------------------------|------------------------------------------|----------------------------------------|----------------------|
| **Software Safety**                  | {extract_relevant_threats("software")} | {extract_relevant_mitigations("software")} | ✅ / ❌ |
| **Communication Security**           | {extract_relevant_threats("communication")} | {extract_relevant_mitigations("communication")} | ✅ / ❌ |
| **Authentication & Access Control**  | {extract_relevant_threats("authentication")} | {extract_relevant_mitigations("authentication")} | ✅ / ❌ |

---

### **📌 Category 2: Equipment Collecting Personal Information (18031-2)**  
#### **Key Compliance Areas**
- **Integrated Access Authentication**: Secure authentication for accessing personal data.  
- **Physical Protection for Authentication Data**: Prevent unauthorized access to stored credentials.  
- **Notifications**: Logging unauthorized access attempts.  
- **External Contact Access**: Prevent unauthorized device connections.  
- **Personal Information Protection**: Encryption, GDPR compliance.  
- **Sensor-Based Data Collection Risks**: Prevent misuse of biometric data.  
- **Special Category Data Handling**: Secure handling of medical, financial records.  

#### **Assessment Table**
| **Requirement**                      | **Identified Issues (Before Mitigations)** | **Confirmed Mitigations (If Provided)** | **Compliance Status** |
|--------------------------------------|------------------------------------------|----------------------------------------|----------------------|
| **Data Protection & Encryption**     | {extract_relevant_threats("encryption")} | {extract_relevant_mitigations("encryption")} | ✅ / ❌ |
| **Secure Authentication**            | {extract_relevant_threats("authentication")} | {extract_relevant_mitigations("authentication")} | ✅ / ❌ |

---

### **📌 Category 3: Financial Asset Equipment (18031-3)**  
#### **Key Compliance Areas**
- **Best Practices**: Secure all financial transactions.  
- **Secure Authentication**: Secure access to financial platforms.  
- **Data Control**: Ensure transaction data integrity.  
- **Audit & Compliance**: Periodic security audits.  
- **Security for Financial Transactions**: Fraud detection, secure API access.  

#### **Assessment Table**
| **Requirement**                      | **Identified Issues (Before Mitigations)** | **Confirmed Mitigations (If Provided)** | **Compliance Status** |
|--------------------------------------|------------------------------------------|----------------------------------------|----------------------|
| **Transaction Security**             | {extract_relevant_threats("transaction")} | {extract_relevant_mitigations("transaction")} | ✅ / ❌ |
| **Fraud Prevention**                 | {extract_relevant_threats("fraud")} | {extract_relevant_mitigations("fraud")} | ✅ / ❌ |

---

## **4. Final Compliance Statement**
- If a RED compliance requirement was not **explicitly analyzed in the threat model, attack tree, or DREAD assessment**, state:  
  **"This compliance requirement was not covered in the provided security assessment and is outside the scope of this evaluation."**

🚀 **Now generate the RED compliance evaluation strictly based on the provided security assessment.**
    """

    return get_expert_analysis(prompt)