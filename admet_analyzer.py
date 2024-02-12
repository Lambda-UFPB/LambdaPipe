import pandas as pd
import numpy as np

class AdmetAnalyzer:
    def __init__(self, csv_path: str):
        self.admet_df = pd.read_csv(csv_path)
        