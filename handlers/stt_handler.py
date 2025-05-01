from openai import OpenAI

class OpenAISpeechHandler:
    def __init__(self, model_preference: str = "whisper-1", api_key: str = None):
        self.api_key = api_key
        self.model_preference = model_preference
        self.client = OpenAI(api_key=self.api_key)
    
    def transcribe_audio(self, audio_file_path: str) -> str:
        try:
            response = self.client.audio.transcriptions.create(
                file=open(audio_file_path, "rb"),
                model=self.model_preference,
                response_format="text"
            )
            transcription = response
            return transcription.strip()
        
        except Exception as e:
            print(f"Error: {e}")
            return "There was an issue transcribing the audio. Please try again."