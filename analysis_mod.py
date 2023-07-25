import praw
import json
import time
from transformers import pipeline, AutoTokenizer, TFAutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from fuzzywuzzy import fuzz

class RedditBot:
    def __init__(self, credentials_path, config_path):
        credentials = self.get_credentials_from_file(credentials_path)
        self.config = self.get_config(config_path)
        self.reddit = praw.Reddit(client_id=credentials[0],
                             client_secret=credentials[1],
                             user_agent=credentials[2],
                             username=credentials[3],
                             password=credentials[4])

    def get_credentials_from_file(self, file_path):
        with open(file_path, "r") as f:
            credentials = f.read().split("|")
        return credentials

    def get_config(self, file_path):
        with open(file_path, "r") as f:
            config = json.load(f)
        return config

    def adhominem_detector(self, text):
        adhominem_pipeline = pipeline("text-classification", model="delboc/ComputationalAdHominemDetection")
        result = adhominem_pipeline(text)
        return result[0]['label'], result[0]['score']

    def bias_detector(self, text):
        tokenizer = AutoTokenizer.from_pretrained("d4data/bias-detection-model")
        model = TFAutoModelForSequenceClassification.from_pretrained("d4data/bias-detection-model")
        bias_pipeline = pipeline("text-classification", model=model, tokenizer=tokenizer)
        result = bias_pipeline(text)
        return result[0]['label'], result[0]['score']

    def sentiment_analyzer(self, text):
        analyzer = SentimentIntensityAnalyzer()
        sentiment = analyzer.polarity_scores(text)
        return sentiment['compound']

    def check_fuzzy_match(self, text, phrases, match_threshold=95):
        for phrase in phrases:
            if fuzz.ratio(phrase, text) > match_threshold:
                return True
        return False

    def process_comments(self):
        subreddits = self.config["subreddits"]
        mod_subs = "+".join(subreddits)
    
        for comment in self.reddit.subreddit(mod_subs).stream.comments(skip_existing=True):
            adhominem_label, adhominem_score = self.adhominem_detector(comment.body)
            bias_label, bias_score = self.bias_detector(comment.body)
            sentiment_score = self.sentiment_analyzer(comment.body)
            is_phrase_match = self.check_fuzzy_match(comment.body, self.config["phrases"])
        
            should_remove = ((adhominem_label == "ADHOMINEM" and adhominem_score > 0.9)
                            or (bias_label == "BIAS" and bias_score > 0.55)
                            or sentiment_score < -0.5
                            or is_phrase_match)
        
            if should_remove:
                comment.mod.remove()
                comment.reply(f"Comment removed due to negative sentiment score: {sentiment_score}, adhominem score: {adhominem_score}, bias score: {bias_score}")
            elif comment.author == "Antibotty":
                parent_comment = comment.parent()
                if isinstance(parent_comment, praw.models.Comment):
                    self.process_antibotty_comment(parent_comment)

    def process_antibotty_comment(self, comment):
        adhominem_label, adhominem_score = self.adhominem_detector(comment.body)
        bias_label, bias_score = self.bias_detector(comment.body)
        sentiment_score = self.sentiment_analyzer(comment.body)
        
        comment.reply(f"Sentiment score: {sentiment_score}, Adhominem score: {adhominem_score}, Bias score: {bias_score}")
        
    def run(self):
        while True:
            self.process_comments()
            time.sleep(1)

if __name__ == "__main__":
    bot = RedditBot('credentials.txt', 'config.json')
    bot.run()
