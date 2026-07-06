import os
import json
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from typing import List

# Define the structured output schema using Pydantic
class SelectedArticleSchema(BaseModel):
    id: int = Field(description="The matching original id integer from the candidate list")
    reading_time: int = Field(description="Estimated reading time in minutes")
    summary: str = Field(description="An expert, high-fidelity 2-sentence summary of this article")

class IntelligenceBriefingSchema(BaseModel):
    synthesis_report: str = Field(description="The complete cross-cutting analysis report formatted in standard GitHub Markdown")
    selected_articles: List[SelectedArticleSchema] = Field(description="Exactly the top 3 chosen articles matching the strict constraints")

# 🔒 Persistent module-level reference to protect active network transport pools
_shared_client = None

def _get_client() -> genai.Client:
    """Instantiates or recovers a global persistent client instance."""
    global _shared_client
    if _shared_client is None:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is missing.")
        _shared_client = genai.Client(api_key=api_key)
    return _shared_client

def generate_synthesis_and_briefing(candidate_articles: list) -> tuple[list, str]:
    """
    Sends the full body text of candidate articles to Gemini 2.5 Flash.
    Returns a tuple of (curated_articles_list, markdown_synthesis_report).
    """
    try:
        client = _get_client()
    except ValueError:
        return [], "# AI Engine Offline\nPlease configure your GEMINI_API_KEY environment variable to enable full-text intelligence synthesis."

    try:
        # Package full content vectors safely for the payload
        pool_data = []
        for idx, art in enumerate(candidate_articles):
            pool_data.append({
                "id": idx,
                "title": art.title,
                "source": art.source,
                "url": art.url,
                "full_content": art.full_text if art.full_text else art.summary
            })

        prompt = f"""
        You are a Director of National Intelligence compiling a high-level systemic briefing for global policymakers.
        Analyze the full-text content of these primary source items collected from open-source RSS channels:
        {json.dumps(pool_data, indent=2)}

        Execute two distinct tasks:
        1. Compile an overarching "Cross-Cutting Intelligence Report" formatted in standard GitHub Markdown for `synthesis_report`.
           - Do NOT simply summarize articles one by one. Group insights.
           - Actively map intersections: highlight analytical convergence or explicit forecasting disagreements between different publications.
           - Ensure clear Markdown layout headers (e.g., ## Core Strategic Vectors, ## Analytical Tensions).
           - Conclude with an actionable 'Key Strategic Takeaways' summary.
           
        2. Filter and rank exactly the top 3 most valuable articles to present as individual deep dives in `selected_articles`. Enforce source diversity (maximum 2 entries from the same brand). Draft an expert 2-sentence summary for each selection.
        """

        # Call Gemini with max token allocation and native response_schema enforcement
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=IntelligenceBriefingSchema,
                temperature=0.3,
                max_output_tokens=15000
            ),
        )

        parsed_data: IntelligenceBriefingSchema = response.parsed
        synthesis_markdown = parsed_data.synthesis_report
        selected_items = parsed_data.selected_articles

        final_articles = []
        for item in selected_items:
            orig_idx = item.id
            if orig_idx is not None and 0 <= orig_idx < len(candidate_articles):
                art = candidate_articles[orig_idx]
                art.reading_time = item.reading_time if item.reading_time else art.reading_time
                art.summary = item.summary if item.summary else art.summary
                final_articles.append(art)

        return final_articles, synthesis_markdown

    except Exception as e:
        return [], f"# Synthesis Pipeline Fallback\nAn error occurred while compiling structured metrics via Gemini: {str(e)}"

def start_adversarial_chat_session(article_title: str, article_source: str, article_text: str):
    """
    Initializes a live, multi-turn Gemini 2.5 Flash chat instance 
    primed to stress-test and critique a specific full-text document.
    """
    client = _get_client()
    
    system_instruction = f"""
    You are an elite, brutally objective geopolitical risk analyst and senior intelligence critic. 
    The user is presenting you with the full text of an article titled '{article_title}' published by '{article_source}'. 
    
    Your mission is to act as an adversarial Q&A engine. Do not simply regurgitate, summarize, or passively validate the article's claims. Instead, your job is to help the user stress-test the analysis. 
    When answering the user's questions or prompts, prioritize uncovering:
    1. Unstated, fragile, or highly vulnerable underlying assumptions made by the author.
    2. Omitted counter-evidence, competing data arrays, or alternative historical precedents the author ignored.
    3. Potential institutional biases, ideological slants, or analytical blind spots.
    4. Strategic second- and third-order implications that the publication downplayed or missed entirely.
    
    Be direct, sharp, intellectually rigorous, and professional. Avoid sycophantic praise or generic introductory filler text. Always anchor your counter-arguments in realistic macroeconomic, geographic, or realpolitik power dynamics.
    
    Here is the primary text source file you are assigned to critique:
    ---
    {article_text}
    ---
    """

    # Spin up an isolated multi-turn chat instance matching the system instructions
    chat = client.chats.create(
        model='gemini-2.5-flash',
        config=types.GenerateContentConfig(
            system_instruction=system_instruction,
            temperature=0.4
        )
    )
    return chat