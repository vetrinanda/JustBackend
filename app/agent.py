import os
from dotenv import load_dotenv
from fastapi import APIRouter,Request
from pydantic import BaseModel
from pydantic_ai import Agent, VideoUrl
from pydantic_ai.models.google import GoogleModel
from pydantic_ai.providers.google import GoogleProvider
from app.auth import user_dependency, get_current_user
from app.limiter import limiter
load_dotenv()
limit=os.getenv("RATE_LIMIT","5/minute")
provider = GoogleProvider(api_key=os.getenv("API_KEY"))
model = GoogleModel('gemini-3-flash-preview', provider=provider)
agent = Agent(model)

router = APIRouter(tags=["Youtube Video QA"])

class VideoInput(BaseModel):
    video_url: str
    question: str


@limiter.limit(limit)
@router.post("/video")
def video(request: Request,video_input: VideoInput, current_user: user_dependency):
    result = agent.run_sync(
        [
            video_input.question,
            VideoUrl(url=video_input.video_url),
        ])
    return result.output
