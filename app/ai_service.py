import os
import json
from google import genai
from google.genai import types

def curate_briefing_with_ai(candidate_articles: list) -> list:
    """
    Sends collected RSS candidate snippets to Gemini 1.5 Flash in ONE batch.
    Asks Gemini to choose the top 3 items enforcing source diversity.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        # Silently return empty list if key isn't configured, triggering the local fallback
        return []
        
    try:
        # Initialize the official Google GenAI Client
        client = genai.Client(api_key=api_key)
        
        # Format candidate items cleanly to preserve token bandwidth
        pool_data = []
        for idx, art in enumerate(candidate_articles):
            pool_data.append({
                "id": idx,
                "title": art.title,
                "source": art.source,
                "url": art.url,
                "snippet": art.summary  # Contains the initial RSS description text
            })

        prompt = f"""
        You are an expert international relations analyst and editor-in-chief of a premium intelligence briefing.
        Review this pool of candidate articles compiled from global RSS feeds:
        {json.dumps(pool_data, indent=2)}
        
        Tasks:
        1. Select exactly the top 3 most impactful or insight-rich articles. Shorter high-quality analytical pieces are acceptable.
        2. CRITICAL: Enforce source diversity. Do not select more than 2 articles from the same source.
        3. For each selected article, draft an expert, professional 2-sentence summary. Sentence 1 must state the core thesis or observation. Sentence 2 must highlight its strategic implication or evidence. 
        4. Estimate a reasonable reading time in minutes based on expected depth.
        
        Return your response strictly as a JSON list matching this structure:
        [
          {{
            "id": <matching_original_id>,
            "reading_time": <int_estimated_minutes>,
            "summary": "<your_expert_2_sentence_summary>"
          }}
        ]
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2
            ),
        )
        
        selections = json.loads(response.text)
        
        final_briefing = []
        for item in selections:
            orig_idx = item.get("id")
            if orig_idx is not None and 0 <= orig_idx < len(candidate_articles):
                art = candidate_articles[orig_idx]
                # Inject the high-fidelity AI components into the existing data model
                art.reading_time = item.get("reading_time", art.reading_time)
                art.summary = item.get("summary", art.summary)
                final_briefing.append(art)
                
        return final_briefing
        
    except Exception as e:
        # Temporary print out the true underlying error to diagnose the issue
        print(f"\n[DIAGNOSTIC ERROR] Gemini API Error: {e}")
        return []