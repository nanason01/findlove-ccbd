from typing import List

import random  # TODO: probably not this


def get_best_candidate(user_id: str, candidate_ids: List[str]) -> str:
    """Return the best candidate_id in candidate_ids for user_id

    Args:
        user_id (str): user to match with
        candidate_ids (List[str]): candidates to match from

    Returns:
        str: id of the best candidate for user_id in candidate_ids
    """
    # TODO @Swati
    return random.choice(candidate_ids)
