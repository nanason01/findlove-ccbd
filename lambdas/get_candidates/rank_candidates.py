from typing import List, Tuple

import random  # TODO: probably not this


def get_best_candidate(user_id: str, candidate_ids: List[str]) -> Tuple[str, str]:
    """Return the best candidate_id in candidate_ids for user_id

    Args:
        user_id (str): user to match with
        candidate_ids (List[str]): candidates to match from

    Returns:
        Tuple[str, str]: id of the best candidate for user_id in candidate_ids,
            reason for matching them to display to the user
    """
    # TODO @Swati
    return random.choice(candidate_ids), 'you were matched for absolutely no reason'
