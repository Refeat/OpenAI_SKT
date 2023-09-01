from embedchain.embedchain import EmbedChain
from embedchain.config import AppConfig
from typing import List

# YoutubeLoader at langchain transcription language fix
from langchain.docstore.document import Document
from langchain.document_loaders import YoutubeLoader

def load_language_fix(self) -> List[Document]:
        """Load documents."""
        try:
            from youtube_transcript_api import (
                NoTranscriptFound,
                TranscriptsDisabled,
                YouTubeTranscriptApi,
            )
        except ImportError:
            raise ImportError(
                "Could not import youtube_transcript_api python package. "
                "Please install it with `pip install youtube-transcript-api`."
            )

        metadata = {"source": self.video_id}

        if self.add_video_info:
            # Get more video meta info
            # Such as title, description, thumbnail url, publish_date
            video_info = self._get_video_info()
            metadata.update(video_info)

        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(self.video_id)
        except TranscriptsDisabled:
            return []

        # detected_language = "en"  # Default to English if language detection fails

        try:
            # Detect the language of the transcript
            for transcript in transcript_list:
                # detected_language = transcript.language_code
                transcript_pieces = transcript.fetch()
                break
        except Exception as e:
            print(f"Language detection failed: {str(e)}")

        transcript = " ".join([t["text"].strip(" ") for t in transcript_pieces])

        return [Document(page_content=transcript, metadata=metadata)]

YoutubeLoader.load = load_language_fix
embed_chain = EmbedChain(config=AppConfig())

