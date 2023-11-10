import openai
from typing import List, Tuple, Dict, Union
import pandas as pd
from models import Engineer
from tqdm import tqdm

class OpenAIAgent:
    def __init__(self, api_key):
        openai.api_key = api_key
        self.model = self.get_latest_model_by_name('GPT-4')[:1][0]
        print(f"Using model: {self.model}")

    def get_latest_model_by_name(self, keyword, topn=3):
        models = [x for x in openai.Model.list()['data'] if keyword.lower() in x['id']]
        latest_models = sorted(models, key=lambda x: x['created'], reverse=True)[:topn]
        return [model['id'] for model in latest_models]

    def get_matching_engineers(self, ticket: Tuple, engineers: pd.DataFrame) -> List[Tuple[Engineer, List[str]]]:
        print(ticket)
        matching_engineers = []

        print(f"len(engineers) : {len(engineers)}")
        for _, engineer in tqdm(engineers.iterrows(),desc="Query AI for mathcing skills"):
            print(f"(engineer) : {engineer}")
            messages = [
                {"role": "system", "content": "You are a highly discerning assistant, "
                                              "aiming for precise and accurate skill matching."},
                {"role": "user", "content": (f"Please analyze the following problem description and skillsets, "
                                               f"and provide a matching score in percentage with 2 decimal places "
                                               f"based on relevance and applicability. Do use 0.0 if skillsets doesn't match!"
                                               f"take advantage of full scales from 0-100, and remember what skillsets you"
                                               f"have scored. If skillsets are the same regardless of text format, give same score."
                                               f"Always reply with a score, Never anything else!!!"
                                               f"\n\n"
                                               f"Problem Description: {ticket[1]}\n"
                                               f"Skillsets: {engineer['skillsets']}\n\n"
                                               f"Matching Score (in percentage):")
                }
            ]

            # Call the OpenAI API using the chat-based model
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                temperature=.2,
            )

            # Extract matched skills from the response
            matched_skills = response['choices'][0]['message']['content'].strip('%')
            if matched_skills:
                matching_engineers.append(({"ticket": ticket, "engineer": engineer, "matching_score": float(matched_skills)}))
                
        # Sorting the engineers based on score in descending order
        matching_engineers.sort(key=lambda x: x["matching_score"], reverse=True)

        #return matching_engineers
        # Convert the list of dictionaries to a DataFrame
        df = pd.DataFrame(matching_engineers)

        # convert the 'engineer' column from Engineer objects to their attributes (Engineer is a class):
        #df = df.join(df['engineer'].apply(lambda x: pd.Series(x.__dict__)).add_prefix('engineer_'))
        #df.drop(columns='engineer', inplace=True)
        return df

