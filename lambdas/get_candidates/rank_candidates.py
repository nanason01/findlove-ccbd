from typing import List, Tuple
from common import users
import random  # TODO: probably not this
# import nltk
# import string
import math
# from collections import Counter


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
    all_users = users.get_users_by_ids(candidate_ids)
    print(all_users)
    # all_users.remove(user)
    
    user_tracks = []
    # user_artists_name = []
    print(user['top_tracks'])
    print(user['top_artists'])
    
    all_users_tracks = []
    # all_users_artists_name = []
    
    for index in range(50):
        track_name = user['top_tracks'][index]['name']
        artist_name = user['top_tracks'][index]['artists'][0]['name']
        user_tracks.append((artist_name, track_name))
        # user_artists_name.append(user['top_artists'][index]['name'])
        
    max_similarity, chosen_candidate, chosen_index = 0, None, None 
    for index1 in range(len(all_users)):
        all_users_tracks.append([])
        # all_users_artists_name.append([])
        for index2 in range(50):
            try:
                track_name = all_users[index1]['top_tracks'][index2]['name']
                artist_name = all_users[index1]['top_tracks'][index2]['artists'][0]['name']
                all_users_tracks[index1].append((artist_name, track_name))
                # all_users_artists_name[index1].append(all_users[index1]['top_artists'][index2]['name'])
            except:
                pass
        print(f"Similarity between {user_id} and {all_users[index1]['id']}: {match_users(user_tracks, all_users_tracks[index1])}")
        similarity = match_users(user_tracks, all_users_tracks[index1])
        if max_similarity <= similarity:
            max_similarity = similarity
            chosen_candidate = all_users[index1]
            chosen_index = index1
    print(str(max_similarity), chosen_candidate, chosen_index)
    
    
    
    
    
    print("After execution")
    print(user_tracks)
    print(all_users_tracks)
    
    return chosen_candidate['id'], f"you were matched with {str(max_similarity)} similarity"


def tokenize(text):
    tokens = [token.lower() for token in text.split() if token.isalpha()]
    #ipdb.set_trace()
    return tokens

def compute_tf(text):
    tokens = tokenize(text)
    tf_dict = {}
    total_tokens = len(tokens)
    
    for token in tokens:
        tf_dict[token] = tf_dict.get(token, 0) + 1
        
    for token, count in tf_dict.items():
        tf_dict[token] = count*1.0 / total_tokens
    #ipdb.set_trace()
    return tf_dict

def compute_idf(documents):
    #print(documents)
    idf_dict = {}
    total_documents = len(documents)
    
    for document in documents:
        # Get unique tokens in the document
        unique_tokens = set(document)
        for token in unique_tokens:
            idf_dict[token] = idf_dict.get(token, 0) + 1
            #ipdb.set_trace()
    # for token, count in idf_dict.items():
    #     idf_dict[token] = math.log(total_documents*1.0 / count)

    return idf_dict

def compute_tf_idf(tf_dict, idf_dict):
    tf_idf_dict = {}
    
    for token, tf in tf_dict.items():
        tf_idf_dict[token] = tf * idf_dict.get(token, 0)
    
    #ipdb.set_trace()
        
    return tf_idf_dict

def cosine_similarity(vec1, vec2):
    intersection = set(vec1.keys()) & set(vec2.keys())
    numerator = sum([vec1[x] * vec2[x] for x in intersection])
    
    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    #ipdb.set_trace()
    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator

def match_users(user1_pref, user2_pref):
    user1_text = ' '.join([' '.join(artist_song) for artist_song in user1_pref])
    user2_text = ' '.join([' '.join(artist_song) for artist_song in user2_pref])

    user1_tf = compute_tf(user1_text)
    user2_tf = compute_tf(user2_text)

    documents = [list(user1_tf.keys()), list(user2_tf.keys())]
    idf_dict = compute_idf(documents)

    user1_tf_idf = compute_tf_idf(user1_tf, idf_dict)
    user2_tf_idf = compute_tf_idf(user2_tf, idf_dict)

    similarity = cosine_similarity(user1_tf_idf, user2_tf_idf)
    
    return similarity