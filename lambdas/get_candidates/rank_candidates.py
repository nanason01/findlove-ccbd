from typing import List, Tuple
from common import users
import random  # TODO: probably not this
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_best_candidate(user_id: str, candidate_ids: List[str]) -> Tuple[str, str]:
    """Return the best candidate_id in candidate_ids for user_id

    Args:
        user_id (str): user to match with
        candidate_ids (List[str]): candidates to match from

    Returns:
        Tuple[str, str]: id of the best candidate for user_id in candidate_ids,
            reason for matching them to display to the user
    """
    
    user = users.get_user(user_id)
    all_users = users.get_all_users()
    
    print(user)
    # print(users.get_all_users())
    all_users.remove(user)
    
    
    print("After deletion")
    print(all_users)
    
    return random.choice(candidate_ids), 'you were matched for absolutely no reason'


