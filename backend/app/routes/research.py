import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from tavily import TavilyClient


ROOT = Path(__file__).resolve().parents[3]

load_dotenv(
    ROOT / "backend" / ".env"
)


router = APIRouter(
    prefix="/api/research",
    tags=["AI Crop Research"]
)


class ResearchRequest(BaseModel):
    question: str
    crop: str | None = None
    topic: str | None = None
    language: str = "en"


def get_tavily_client():
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail="TAVILY_API_KEY is not configured."
        )

    return TavilyClient(
        api_key=api_key
    )


@router.post("")
async def research(
    data: ResearchRequest
):
    question = data.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Research question is required."
        )

    crop = (
        data.crop.strip()
        if data.crop
        else "General Agriculture"
    )

    topic = (
        data.topic.strip()
        if data.topic
        else "Agriculture"
    )

    language = (
        data.language or "en"
    ).lower()

    # --------------------------------------------------
    # Search query
    # Keep it short and focused.
    # --------------------------------------------------

    if language == "te":
        query = (
            f"{question} "
            f"{crop} "
            f"{topic} "
            "agriculture farmer India crop management "
            "pest disease fertilizer pesticide"
        )
    else:
        query = (
            f"{question} "
            f"{crop} "
            f"{topic} "
            "agriculture farmer India crop management "
            "pest disease fertilizer pesticide"
        )

    # These are PREFERRED sources, NOT restrictions.
    preferred_domains = [
        "icar.gov.in",
        "agritech.tnau.ac.in",
        "agritech.kau.in",
        "fao.org",
        "mausam.imd.gov.in",
        "imd.gov.in"
    ]

    try:
        client = get_tavily_client()

        result = client.search(
            query=query,
            search_depth="advanced",
            max_results=10,

            # Prefer trusted agricultural sources,
            # but allow other websites too.
            include_domains=preferred_domains,
            include_domains_mode="prefer",

            # Prefer Indian information.
            country="india",

            # Allow relevant agricultural sources in different languages.
            # This helps when Telugu-language search results are limited.

            # Let Tavily synthesize an answer.
            include_answer="advanced"
        )

        answer = (
            result.get("answer")
            or ""
        ).strip()

        results = result.get(
            "results",
            []
        )

        sources = []

        for item in results:

            url = item.get(
                "url",
                ""
            )

            title = item.get(
                "title",
                "Source"
            )

            content = item.get(
                "content",
                ""
            )

            if url:
                sources.append({
                    "title": title,
                    "url": url,
                    "content": content
                })

        # --------------------------------------------------
        # If Tavily does not produce an answer
        # --------------------------------------------------

        if not answer:

            if language == "te":
                answer = (
                    "క్షమించండి. ఈ ప్రశ్నకు "
                    "వెబ్‌లో సరైన వ్యవసాయ సమాచారం "
                    "ప్రస్తుతం దొరకలేదు. "
                    "దయచేసి ప్రశ్నను మరింత స్పష్టంగా "
                    "అడగండి."
                )

            else:
                answer = (
                    "Sorry. I could not find enough "
                    "reliable information on the web "
                    "for this question."
                )

        return {
            "success": True,
            "answer": answer,
            "sources": sources,
            "provider": "Tavily Web Search",
            "language": language,
            "crop": crop,
            "topic": topic
        }

    except HTTPException:
        raise

    except Exception as exc:

        print(
            "RESEARCH ERROR:",
            repr(exc)
        )

        raise HTTPException(
            status_code=500,
            detail="Research request failed."
        )