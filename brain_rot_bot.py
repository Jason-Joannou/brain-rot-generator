import json
import random
import os
from datetime import datetime
from dotenv import load_dotenv
from google import genai
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip
from gtts import gTTS

load_dotenv()

class BrainRotBot:
    def __init__(self):
        
        # load topics from JSON file
        self.topics = self._load_topics_from_json()
        self.selected_video = self._load_background_video()
        self.selected_topic = self._load_selected_topic()
        self.genai_client = self


    def _load_topics_from_json(self):
        try:
            with open('topics.json', 'r') as file:
                topics = json.load(file)
            return topics
        except FileNotFoundError:
            print("Error: topics.json file not found.")
            raise FileNotFoundError("There is no topics.json file")
        
    def _load_background_video(self):
        # Define base videos
        base_videos = ['video1.mp4', 'video2.mp4', 'video3.mp4']

        # Select a video
        selected_video = random.choice(base_videos)
        return selected_video
    
    def _load_selected_topic(self):
        current_day = datetime.now().strftime('%A')
        selected_topic = random.choice(self.topics.get(current_day, []))
        return selected_topic
    
    def _load_genai_client(self):
        try:
            client = genai.Client(os.getenv('GEMINI_API_KEY'))
            return client
        except Exception as e:
            print(f"Error: {e}")
            raise Exception("There is no GEMINI_API_KEY")
        
    def generate_content(self):
        prompt = (
            f"Create an engaging and captivating script for a TikTok video about {self.selected_topic}. "
            f"The target audience is young adults aged 18-30 who are interested in {self.selected_topic}. "
            f"The script should be concise, entertaining, and informative, aiming to capture attention within the first few seconds. "
            f"Include a call to action to encourage viewers to like, comment, and share the video."
        )
        response = self.genai_client.generate(prompt=prompt)
        generated_text = response['text'].strip()
        return generated_text
    
    def convert_text_to_speech(self, text):
        tts = gTTS(text=text, lang='en')
        audio_file = 'audio.mp3'
        tts.save(audio_file)
        return audio_file
    
    def create_video(self, text, audio_file):
        video_clip = VideoFileClip(self.selected_video)
        audio_clip = AudioFileClip(audio_file)
        video_with_audio = video_clip.set_audio(audio_clip)

        text_clip = TextClip(text, fontsize=24, color='white', bg_color='black', size=video_clip.size)
        text_clip = text_clip.set_position('bottom').set_duration(video_clip.duration)

        final_clip = CompositeVideoClip([video_with_audio, text_clip])

        output_path = 'upload/final_video_with_text.mp4'
        final_clip.write_videofile(output_path, codec='libx264')

        os.remove(audio_file)

    def run(self):
        generated_text = self.generate_content()
        audio_file = self.convert_text_to_speech(generated_text)
        self.create_video(generated_text, audio_file)

    
