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

def generate_synthesis_and_briefing(candidate_articles: list) -> tuple[list, str]:
    """
    Sends the full body text of candidate articles to Gemini 2.5 Flash.
    Returns a tuple of (curated_articles_list, markdown_synthesis_report).
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return [], "# AI Engine Offline\nPlease configure your GEMINI_API_KEY environment variable to enable full-text intelligence synthesis."

    try:
        client = genai.Client(api_key=api_key)
        
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
        You are a Director of National Intelligence compiling a high-level systemic briefing for Singaporean policymakers.
        Analyze the full-text content of these primary source items collected from open-source RSS channels:
        {json.dumps(pool_data, indent=2)}

        Execute two distinct tasks:
        1. Compile an overarching "Cross-Cutting Intelligence Report" formatted in standard GitHub Markdown for `synthesis_report`.
           - Do NOT simply summarize articles one by one. Group insights by grand-strategic themes, macroeconomic vectors, or regional security architectures, for example.
           - Actively map intersections: highlight analytical convergence or explicit forecasting disagreements between different publications.
           - Ensure clear Markdown layout headers (e.g., ## Core Strategic Vectors, ## Analytical Tensions).
           - Conclude with an actionable 'Key Strategic Takeaways' summary.
           
        2. Filter and rank exactly the top 3 most valuable articles to present as individual deep dives in `selected_articles`. Enforce source diversity (maximum 2 entries from the same brand). Draft an expert 2-sentence summary for each selection.
        """

        # Call Gemini with native response_schema enforcement
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=IntelligenceBriefingSchema,
                temperature=0.3,
                max_output_tokens=9000
            ),
        )

        # The SDK automatically parses the schema safely into response.parsed
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