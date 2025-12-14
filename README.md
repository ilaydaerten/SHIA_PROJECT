# SHIA – Smart Household Intelligent Agent

SHIA (Smart Household Intelligent Agent) is an **offline, rule-based intelligent agent system**
designed to autonomously manage household devices while preserving full human control.
The project is developed as part of the **Intelligent Agents (IA)** course.

This system is **NOT a generative AI or machine learning application**.
Instead, it demonstrates intelligent agent principles such as perception, reasoning,
action, policy validation, and human-in-the-loop control.

---

##  Project Objectives

- Design an **intelligent agent** for smart home management
- Apply **structured Prompt Engineering** as contextual decision input
- Ensure **explainable and deterministic decision-making**
- Support **manual user overrides and device locking**
- Improve comfort, safety, and energy efficiency

---

##  Intelligent Agent Approach

SHIA follows the **Perception–Decision–Action** loop:

1. **Perception**
   - Simulated sensors: temperature, humidity, light level, occupancy
2. **Decision**
   - Rule-based reasoning using structured decision contexts (prompts)
   - Trend analysis and short-term memory
3. **Action**
   - Device control subject to policy validation
   - Manual locks override autonomous behavior

> Prompt Engineering in SHIA refers to **structured contextual inputs**, not natural language prompts.

---

## ⚙️ System Architecture

Main modules:
- `sensors.py` – Environment perception and simulation
- `agent.py` – Intelligent decision-making logic
- `policy_manager.py` – Safety and energy constraints
- `devices.py` – Device simulation and energy tracking
- `app.py` – Streamlit-based user interface and control dashboard

---

##  Key Features

- Offline operation (no internet, no API keys)
- Human-in-the-loop control
- Manual device overrides with AI lock mechanism
- Trend-aware decision making
- Real-time visualization via Streamlit
- Transparent decision explanations and logs

---

##  Testing & Evaluation

The system is evaluated through:
- Scenario-based testing
- Input/output verification and validation
- Error compounding tests
- Analysis of decision quality, stability, and processing time

All decisions and sensor values are logged and displayed on the dashboard.

---

##  Limitations

- Fully simulated environment (no real hardware integration)
- Single-agent architecture
- No natural language or voice interaction
- No machine learning or LLM usage

---

## 🚀 How to Run the Project

```bash
pip install -r requirements.txt
streamlit run app.py
