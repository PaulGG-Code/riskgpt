import streamlit as st
import requests
import google.generativeai as genai
from openai import OpenAI, AzureOpenAI
from anthropic import Anthropic
from mistralai import Mistral
from groq import Groq

def get_expert_analysis(prompt):
    provider = st.session_state.get("model_provider", "OpenAI API")
    expert_analysis = ""
    
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

def run_expert_agent():
    prompt = f"""
You are a cybersecurity and EU regulatory compliance expert specializing in the Radio Equipment Directive (RED, Directive 2014/53/EU), 
with a deep focus on Articles 3.3(d), 3.3(e), and 3.3(f). Your task is to analyze the compliance of a specific product under evaluation (ToE) 
using dynamic risk assessment outputs from our analysis (which may include an architectural diagram, a system description, or GitHub repository data). 

Please produce a comprehensive "before vs. after" analysis that includes:

1. **Overall Compliance Summary:**  
   - A brief statement of the current risk posture and major compliance gaps with respect to RED.

2. **Risk Posture Before Mitigations:**  
   - **Key Threats & Non-compliance Issues:**  
     - *Article 3.3(d):* Issues related to network integrity and resource misuse.
     - *Article 3.3(e):* Issues related to data protection and privacy.
     - *Article 3.3(f):* Issues related to fraud prevention.
   - **Detailed Reasoning (Before):**  
     - Explain in detail the risks and gaps observed (include DREAD scores if available).

3. **Risk Posture After Mitigations:**  
   - **Implemented Mitigations & Improvements:**  
     - *Article 3.3(d):* Detail improvements such as enhanced encryption, rate limiting, or secure firmware updates.
     - *Article 3.3(e):* Detail improvements such as improved authentication, secure data transmission, or comprehensive logging.
     - *Article 3.3(f):* Detail improvements such as anti-fraud measures and secure API controls.
   - **Detailed Reasoning (After):**  
     - Explain how these mitigations address the compliance gaps.

4. **Table Comparison:**  
   - Provide a Markdown table that visually summarizes the key differences between the "Before" and "After" states for each RED article:
     
     | RED Article     | Before Mitigations                                    | After Mitigations                                     | Key Improvement Summary                     |
     |-----------------|-------------------------------------------------------|-------------------------------------------------------|---------------------------------------------|
     | **3.3(d)**     | [Issues regarding network integrity/resource misuse]  | [Improvements in network protection measures]       | [Summary of improvements]                   |
     | **3.3(e)**     | [Issues regarding data protection and privacy]        | [Improvements in encryption and access controls]      | [Summary of improvements]                   |
     | **3.3(f)**     | [Issues regarding fraud prevention]                   | [Improvements in anti-fraud and secure transactions]  | [Summary of improvements]                   |

Generate your comprehensive "before vs. after" RED compliance analysis now, including the table comparison.
    
**Risk Assessment Outputs:**

**Threat Model:**  
{st.session_state.get("threat_model", "Not available")}

**Attack Tree:**  
{st.session_state.get("attack_tree", "Not available")}

**Mitigations:**  
{st.session_state.get("mitigations", "Not available")}

**DREAD Assessment:**  
{st.session_state.get("dread_assessment", "Not available")}

**Test Cases:**  
{st.session_state.get("test_cases", "Not available")}

Please include detailed reasoning and justification in your analysis.
    """
    return get_expert_analysis(prompt)
