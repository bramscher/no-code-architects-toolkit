from flask import Blueprint, Response
from app_utils import validate_payload, queue_task_wrapper
from services.v1.video.youtube_transcript import fetch_youtube_transcript
from services.authentication import authenticate

v1_video_youtube_transcript_bp = Blueprint('v1_video_youtube_transcript', __name__)

@v1_video_youtube_transcript_bp.route('/v1/video/youtube/transcript', methods=['POST'])
@authenticate
@validate_payload({
    "type": "object",
    "properties": {
        "youtube_url": {"type": "string"},
        "languages": {"type": "array", "items": {"type": "string"}},
        "format": {"type": "string", "enum": ["json", "plain", "srt"]},
        "response_type": {"type": "string", "enum": ["direct", "cloud"]}
    },
    "required": ["youtube_url"],
    "additionalProperties": False
})
@queue_task_wrapper(bypass_queue=False)
def youtube_transcript(job_id, data):
    youtube_url = data['youtube_url']
    languages = data.get('languages')
    format = data.get('format', 'json')
    response_type = data.get('response_type', 'direct')
    result = fetch_youtube_transcript(youtube_url, languages, format, response_type, job_id)
    if isinstance(result, Response):
        result_data = result.get_json()
        if "error" in result_data:
            return result, "/v1/video/youtube/transcript", 400
        # If not an error, return the response as is
        return result, "/v1/video/youtube/transcript", 200
    if "error" in result:
        return result, "/v1/video/youtube/transcript", 400
    return result, "/v1/video/youtube/transcript", 200 