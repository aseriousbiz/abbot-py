import os

def get_skill_api_url(skill_id):
    base_url = os.environ.get('AbbotApiBaseUrl', 'https://localhost:4979/api')
    return f'{base_url}/skills/{skill_id}'

def get_reply_url(skill_id):
    api_url = get_skill_api_url(skill_id)
    return f'{api_url}/reply'
