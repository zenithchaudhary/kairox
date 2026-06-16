from pydantic import BaseModel, Field
from src.analysis.grok_client import get_client, GROK_MODEL


class ArticleAnalysis(BaseModel):
    """
    Schema enforced by xAI's Structured Outputs feature. The response
    is guaranteed to match these fields exactly, no manual JSON parsing.
    """
    summary: str = Field(
        description="A neutral 2-3 sentence summary of the article"
    )
    suggested_angle: str = Field(
        description=(
            "One sentence on what this article means for capital allocation: "
            "who benefits, who is hurt, and why it matters to a trader"
        )
    )
    relevance_score: int = Field(
        description=(
            "Relevance score from 1 to 10 for how significant this story is "
            "to financial markets. 1 = routine/minor, 10 = major market-moving event"
        ),
        ge=1,
        le=10,
    )


SYSTEM_PROMPT = (
    "You are a financial news analyst writing for a swing trader audience. "
    "Given a news article, assess it neutrally and concisely."
)

# Common disclosure/disclaimer language financial sites prepend or
# append to articles. Not the actual content, filtered out before
# picking lead/closing paragraphs.
#
# KNOWN LIMITATION: this is a keyword list, not a real classifier.
# Every site phrases disclaimers differently, so some will slip through
# (seen in testing: "for educational purposes" vs "for informational
# purposes" was enough to dodge an earlier version of this list).
# Treated as acceptable for this project rather than chased to 100%.
BOILERPLATE_MARKERS = (
    "advertiser disclosure",
    "affiliate link",
    "advertisers who pay",
    "may receive compensation",
    "not financial advice",
    "not investment advice",
    "for informational purposes",
    "for educational purposes",
    "editorial disclaimer",
    "consult a qualified",
)


def _is_boilerplate(paragraph: str) -> bool:
    lowered = paragraph.lower()
    return any(marker in lowered for marker in BOILERPLATE_MARKERS)


def condense_for_analysis(full_text: str, source_name: str) -> str:
    """
    Reduces full article text to its lead and closing paragraphs before
    sending to Grok. Filters out common disclosure boilerplate first,
    since financial sites often sandwich the real content between
    disclaimers at the top and bottom.
    """
    paragraphs = [p.strip() for p in full_text.split("\n") if p.strip()]
    paragraphs = [p for p in paragraphs if not _is_boilerplate(p)]

    if not paragraphs:
        return f"Source: {source_name}\n\n"

    if len(paragraphs) == 1:
        condensed = paragraphs[0]
    else:
        condensed = paragraphs[0] + "\n\n" + paragraphs[-1]

    return f"Source: {source_name}\n\n{condensed}"


def analyze_article(headline: str, body: str) -> ArticleAnalysis:
    """
    Sends an article to Grok and returns a structured analysis.
    Raises if the API call fails — caller is responsible for handling
    that (see Block 23, retry logic).
    """
    client = get_client()

    completion = client.beta.chat.completions.parse(
        model=GROK_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Headline: {headline}\n\nArticle: {body}"},
        ],
        response_format=ArticleAnalysis,
    )

    return completion.choices[0].message.parsed