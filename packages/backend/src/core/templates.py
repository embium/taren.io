from typing import Dict, List
from pydantic import BaseModel


class AnalysisTemplate(BaseModel):
    id: str
    name: str
    description: str
    instructions: str


TEMPLATES: List[AnalysisTemplate] = [
    AnalysisTemplate(
        id="pain_points",
        name="Pain Points & Frustrations",
        description="Identify common struggles, unmet needs, and frustrations expressed by users.",
        instructions=(
            "Identify distinct pain points and frustrations expressed by users. "
            "For each pain point, explain what the underlying issue is, how widespread it feels, "
            "and why existing solutions are failing them."
        ),
    ),
    AnalysisTemplate(
        id="feature_requests",
        name="Feature Requests",
        description="Extract features or capabilities users are asking for or trying to build themselves.",
        instructions=(
            "Identify specific features, tools, or capabilities that users are requesting, "
            "wishing for, or attempting to build themselves. For each feature request, explain "
            "the use case and what problem the feature would solve."
        ),
    ),
    AnalysisTemplate(
        id="competitors",
        name="Competitor Mentions",
        description="Find mentions of competitors, alternative products, and what users like or dislike about them.",
        instructions=(
            "Identify mentions of competitor products, alternative solutions, or existing tools. "
            "For each competitor mentioned, extract what users like or dislike about it, "
            "and any reasons given for switching to or away from it."
        ),
    ),
    AnalysisTemplate(
        id="use_cases",
        name="Unconventional Use Cases",
        description="Discover unique or unexpected ways people are using products or solving problems.",
        instructions=(
            "Identify unconventional, unique, or unexpected ways users are solving problems "
            "or using products. Focus on hacks, workarounds, and novel use cases that might "
            "indicate an underserved niche."
        ),
    ),
    AnalysisTemplate(
        id="sentiment",
        name="General Sentiment",
        description="Analyze the overall mood, consensus, and prevailing opinions on topics.",
        instructions=(
            "Identify the prevailing sentiments, moods, and consensuses within the community. "
            "Group the findings by specific topics or opinions, explaining why the community "
            "feels strongly about each one."
        ),
    ),
    AnalysisTemplate(
        id="questions",
        name="Common Questions",
        description="Extract frequently asked questions, areas of confusion, and requests for help.",
        instructions=(
            "Identify frequently asked questions, areas of deep confusion, and common requests "
            "for help. Explain the context behind the questions and what specific knowledge "
            "gap they represent."
        ),
    ),
]

def get_template_by_id(template_id: str) -> AnalysisTemplate | None:
    for t in TEMPLATES:
        if t.id == template_id:
            return t
    return None
