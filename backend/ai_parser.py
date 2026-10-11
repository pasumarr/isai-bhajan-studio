import os
import json
import logging
from google import genai

logger = logging.getLogger(__name__)

def parse_search_intent(prompt: str) -> dict:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY is not set. Returning mock intent.")
        return {
            "semantic_query": prompt,
            "tempo": "",
            "deity": "",
            "ragas": [],
            "mood": ""
        }
    
    try:
        client = genai.Client(api_key=api_key)
        
        system_instruction = """You are an expert at parsing search queries for a Bhajan (devotional song) app.
Extract the following information from the user's prompt and return ONLY valid JSON with these keys:
- "semantic_query": The core meaning, story, or message they are looking for, stripped of generic filter words.
- "tempo": Extract if they want "slow", "medium", or "fast". (Map terms like "fast paced" to "fast", "calm" to "slow", etc). If not specified, use "".
- "deity": The deity they are looking for (e.g., shiva, ganesha, krishna, rama, sai, guru, devi). Use lowercase. If not specified, use "".
- "ragas": A JSON array of musical ragas. If the user asks for "minor", "melancholy", or "sad", output corresponding minor ragas: ["shivaranjani", "charukesi", "darbari", "bhairavi", "todi", "revati", "abheri", "malkauns", "madhuvanti", "natabhairavi", "sindhu bhairavi"]. If they ask for "major", "happy", or "upbeat", output major ragas: ["mohanam", "shankarabharanam", "kalyani", "bilawal", "hamsadhvani", "yaman", "bhoopali"]. If they specify a raga directly, include it. If not specified, use [].
- "mood": The emotional mood (e.g., peaceful, energetic, melancholy, joyful). If not specified, use "".

Return ONLY valid JSON, no markdown, no explanation."""

        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=system_instruction + "\n\nUser Query: " + prompt,
        )
        
        # Parse the JSON response, stripping any markdown fences
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        
        intent = json.loads(text)
        logger.info(f"Parsed intent: {intent}")
        return intent
    except Exception as e:
        logger.error(f"Error parsing intent: {e}")
        return {
            "semantic_query": prompt,
            "tempo": "",
            "deity": "",
            "ragas": [],
            "mood": ""
        }

