import json
import random
import os
from datetime import datetime

class BrainRotBot:
    def __init__(self):
        
        # load topics from JSON file
        self.topics = self.load_topics_from_json()


    def load_topics_from_json():
        try:
            with open('topics.json', 'r') as file:
                topics = json.load(file)
            return topics
        except FileNotFoundError:
            print("Error: topics.json file not found.")
            raise FileNotFoundError("There is no topics.json file")
