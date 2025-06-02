# Define custom ML classes here

import pandas as pd
import numpy as np
from textblob import TextBlob
import re

class DynamicOutlierHandler:
    def __init__(self, lower_quantile=0.01, upper_quantile=0.99):
        self.lower_quantile = lower_quantile
        self.upper_quantile = upper_quantile

    def fit(self, X, y=None):
        self.quantiles_ = {
            col: (X[col].quantile(self.lower_quantile), X[col].quantile(self.upper_quantile))
            for col in X.columns if pd.api.types.is_numeric_dtype(X[col])
        }
        return self

    def transform(self, X):
        X = X.copy()
        for col, (lower, upper) in self.quantiles_.items():
            X[col] = X[col].clip(lower=lower, upper=upper)
        return X

class SentimentAnalyzer:
    def fit(self, X, y=None): return self

    def transform(self, X):
        X = X.copy()
        X['Polarity'] = X['ExitStatement'].apply(lambda t: TextBlob(t).polarity if pd.notnull(t) else None)
        X['Subjectivity'] = X['ExitStatement'].apply(lambda t: TextBlob(t).subjectivity if pd.notnull(t) else None)
        return X

class TextCleaner:
    def fit(self, X, y=None): return self

    def transform(self, X): return X.apply(self._clean_text)

    def _clean_text(self, text):
        text = text.lower()
        text = re.sub(r"[^a-zA-Z0-9\s]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text 