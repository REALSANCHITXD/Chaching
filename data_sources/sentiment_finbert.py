import logging

logger = logging.getLogger(__name__)

class FinBERTSentiment:
    def __init__(self):
        self.pipe = None

    def _ensure_loaded(self):
        """
        Lazy load the HuggingFace transformers pipeline only when needed.
        """
        if self.pipe is not None:
            return
            
        try:
            from transformers import pipeline
            self.pipe = pipeline("sentiment-analysis", model="yiyanghkust/finbert-tone")
        except Exception as e:
            logger.error(f"Sentiment model failed to load: {e}")
            self.pipe = False

    async def analyze_per_asset(self, queries):
        """
        Analyze the sentiment of a given list of asset queries.
        Returns a dictionary mapping the query to its sentiment score.
        """
        results = {}
        self._ensure_loaded()
        
        for query in queries:
            # Extract the ticker/symbol from the query if needed
            term = f"{query.split('.')[0]} stock news"
            
            try:
                if not self.pipe:
                    raise RuntimeError("Sentiment pipeline is unavailable.")
                    
                # The model returns a list containing a dict, e.g. [{'label': 'Positive', 'score': 0.99}]
                res = self.pipe(term)[0]
                results[query] = {
                    'label': res['label'],
                    'score': res['score']
                }
            except Exception as e:
                logger.warning(f"Failed to analyze sentiment for {query}: {e}. Defaulting to neutral.")
                results[query] = {
                    'label': 'neutral',
                    'score': 0.0
                }
                
        return results
