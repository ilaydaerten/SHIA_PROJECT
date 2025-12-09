import json
import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

class SHIADecisionAgent:
    def __init__(self):
        # .env dosyasından okunan anahtar ortam değişkenlerinde olmalı
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo", 
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

    def decide(self, sensor_data):
        """Sensör verisini analiz eder ve JSON karar üretir."""
    
        # Belgedeki Prompt Formatı 
        prompt = f"""
        Act as the SHIA (Smart Household Intelligent Agent). 
        Analyze the following sensor data: {sensor_data}

        Your Task:
        1. If temperature > 25 and occupancy is True -> Turn 'ac_main' to 'ON'.
        2. If temperature < 19 and occupancy is True -> Turn 'heater_main' to 'ON'.
        3. If occupancy is False -> Turn all devices 'OFF'.
        4. If it is dark (light < 100) and occupancy is True -> Turn 'lights_living' to 'ON'.
        5. Otherwise -> 'IDLE'.

        Return ONLY a JSON object. Do not add any text.
        Format:
        {{
            "device_id": "device_name_or_all",
            "action": "ON/OFF/IDLE",
            "reason": "Brief explanation",
            "timestamp": "ISO Format"
        }}
        """

        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            # JSON temizleme (bazen markdown ```json ile gelir)
            content = response.content.replace("```json", "").replace("```", "").strip()
            return json.loads(content)
        except Exception as e:
            return {"device_id": "error", "action": "IDLE", "reason": str(e)}

    def reflect(self, last_decision, sensor_data):
        """Performance Review Module[cite: 10]: Geçmiş kararı eleştirir."""
        prompt = f"Review this action: {last_decision} under conditions: {sensor_data}. Was this energy efficient? Answer in 1 short sentence."
        response = self.llm.invoke([HumanMessage(content=prompt)])
        return response.content