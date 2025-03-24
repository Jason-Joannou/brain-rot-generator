import json
import random
import os
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, CompositeAudioClip
from gtts import gTTS
import argparse  # Add this for CLI support

load_dotenv()

class BrainRotBot:
    def __init__(self):
        # load topics from JSON file
        self.topics = self._load_topics_from_json()
        self.selected_video = self._load_background_video()
        self.selected_topic = self._load_selected_topic()
        self._configure_genai()

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
        base_videos = ['./videos/subway_surfer.mp4']

        # Select a video
        selected_video = random.choice(base_videos)
        return selected_video
    
    def _load_selected_topic(self):
        current_day = datetime.now().strftime('%A')
        selected_topic = random.choice(self.topics.get(current_day, []))
        return selected_topic
    
    def _configure_genai(self):
        # Configure the genai module with your API key
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is not set")
            genai.configure(api_key=api_key)
        except Exception as e:
            print(f"Error configuring Gemini API: {e}")
            raise
        
    def generate_content(self):
        # Create a model instance directly from the genai module
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = (
            f"Create an engaging and captivating script which you will narate for a TikTok video about {self.selected_topic}. "
            f"The target audience is young adults aged 18-30 who are interested in {self.selected_topic}. "
            f"The naration should be concise, entertaining, informative, and exactly a minute long - aiming to capture attention within the first few seconds. "
            f"Include a call to action to encourage viewers to like, comment, and share the video."
        )
        response = model.generate_content(prompt)
        generated_text = response.text.strip()
        return generated_text
    
    def convert_text_to_speech(self, text):
        tts = gTTS(text=text, lang='en')
        audio_file = 'audio.mp3'
        tts.save(audio_file)
        return audio_file
    
    def create_video(self, text, audio_file):
        # Ensure the upload directory exists
        os.makedirs('upload', exist_ok=True)
        
        video_clip = VideoFileClip(self.selected_video)
        audio_clip = AudioFileClip(audio_file)
        new_audio_clip = CompositeAudioClip([audio_clip])
        video_clip.audio = new_audio_clip
        font = os.getenv('FONT_FILE')
        text_clip = TextClip(font=font, text=text, font_size=24, color='white', bg_color='black', size=video_clip.size, duration=video_clip.duration, method='caption')
        # text_clip = text_clip.set_position('bottom').set_duration(video_clip.duration)

        final_clip = CompositeVideoClip([video_clip, text_clip])

        output_path = 'upload/final_video_with_text.mp4'
        final_clip.write_videofile(output_path, codec='libx264')

        os.remove(audio_file)
        return output_path

    def run(self, specific_day=None, specific_topic=None):
        if specific_day:
            current_day = specific_day
        else:
            current_day = datetime.now().strftime('%A')
            
        if specific_topic:
            self.selected_topic = specific_topic
        else:
            self.selected_topic = random.choice(self.topics.get(current_day, []))
            
        print(f"Generating content for topic: {self.selected_topic}")
        generated_text = self.generate_content()
        print("Content generated successfully")
        
        print("Converting text to speech...")
        audio_file = self.convert_text_to_speech(generated_text)
        
        print("Creating video...")
        output_path = self.create_video(generated_text, audio_file)
        print(f"Video created successfully at: {output_path}")
        return output_path

# CLI interface
def main():
    parser = argparse.ArgumentParser(description='Generate TikTok videos automatically')
    parser.add_argument('--day', type=str, help='Specify a day of the week (e.g., Monday)')
    parser.add_argument('--topic', type=str, help='Specify a specific topic')
    args = parser.parse_args()
    
    bot = BrainRotBot()
    bot.run(specific_day=args.day, specific_topic=args.topic)

if __name__ == "__main__":
    main()