import pandas as pd
import numpy as np
import json
import os
from src.utils.logger import get_logger
from src.utils.llm_client import LLMClient

logger = get_logger("DataAgent")

class DataAgent:
    def __init__(self, config):
        self.path = config['data']['path']
        self.config = config
        self.df = None
        self.llm = LLMClient(config)

    def _normalize_with_llm(self, unique_names):
        logger.info(f"Asking AI to standardize {len(unique_names)} unique campaign variations...")
        system_prompt = """
        You are a Data Quality Expert. Map inconsistent campaign names to their standard versions.
        Return ONLY a valid JSON object: {"messy_name": "Standard Name"}.
        """
        user_content = f"List: {json.dumps(unique_names)}"
        
        response = self.llm.generate(system_prompt, user_content)
        try:
            clean_json = response.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"AI Cleaning failed: {e}")
            return {name: name for name in unique_names}

    def load_and_clean(self):
        logger.info(f"Loading data from {self.path}...")
        try:
            # Check for Sample Mode
            if self.config['data'].get('use_sample_data', False):
                limit = self.config['data'].get('sample_size', 50)
                logger.warning(f"⚠️ SAMPLE MODE ACTIVE: Loading only first {limit} rows.")
                self.df = pd.read_csv(self.path, nrows=limit)
            else:
                self.df = pd.read_csv(self.path)
            
            # AI Normalization
            unique_names = self.df['campaign_name'].unique().tolist()
            if unique_names:
                cleaning_map = self._normalize_with_llm(unique_names)
                self.df['campaign_name'] = self.df['campaign_name'].map(cleaning_map).fillna(self.df['campaign_name'])

            self.df['date'] = pd.to_datetime(self.df['date'], dayfirst=True)
            
            for col in ['spend', 'revenue', 'clicks', 'purchases']:
                self.df[col] = self.df[col].fillna(0)
            
            self.df['roas'] = np.where(self.df['spend'] > 0, self.df['revenue'] / self.df['spend'], 0)
            
            logger.info(f"Successfully loaded {len(self.df)} rows.")
            return self.df
            
        except FileNotFoundError:
            logger.error(f"File not found.")
            raise

    def get_performance_summary(self):
        if self.df is None: raise ValueError("Data not loaded.")
        max_date = self.df['date'].max()
        last_7 = max_date - pd.Timedelta(days=7)
        prev_7 = last_7 - pd.Timedelta(days=7)

        current = self.df[self.df['date'] > last_7]
        previous = self.df[(self.df['date'] <= last_7) & (self.df['date'] > prev_7)]

        summary = {
            "period_end_date": str(max_date.date()),
            "current_roas": round(current['roas'].mean(), 2) if not current.empty else 0,
            "previous_roas": round(previous['roas'].mean(), 2) if not previous.empty else 0,
            "spend_change_percent": 0.0,
            "worst_campaign_by_roas": "N/A"
        }
        
        if not previous.empty and previous['spend'].sum() > 0:
            summary["spend_change_percent"] = round(((current['spend'].sum() - previous['spend'].sum()) / previous['spend'].sum()) * 100, 2)
            
        if not current.empty:
            summary["worst_campaign_by_roas"] = current.groupby('campaign_name')['roas'].mean().idxmin()
            
        return summary

    def get_bad_creatives(self):
        threshold = self.config['thresholds']['low_ctr']
        recent_df = self.df[self.df['date'] > (self.df['date'].max() - pd.Timedelta(days=30))]
        bad_ads = recent_df[recent_df['ctr'] < threshold].copy()
        return bad_ads.drop_duplicates(subset=['creative_message'])[['campaign_name', 'creative_message', 'ctr']].head(5).to_dict(orient='records')