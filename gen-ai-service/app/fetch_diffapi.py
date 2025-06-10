from rag_query import run_rag_query

import requests

def get_response(PROJECT_ID, MR_IID):
    # Headers
    headers = {
        "PRIVATE-TOKEN": PRIVATE_TOKEN
    }

    # Endpoint for MR diff (changes)
    url = f"{GITLAB_API_URL}/projects/{PROJECT_ID}/merge_requests/{MR_IID}/changes"

    # API Call
    response = requests.get(url, headers=headers)

    # Check and process response
    if response.status_code == 200:
        mr_data = response.json()
        print(f"Title: {mr_data['title']}")
        print(f"Author: {mr_data['author']['name']}")
        print(f"Total files changed: {len(mr_data['changes'])}")
        print("=" * 80)
        answer = ""
        for change in mr_data['changes']:
            diff = ""
            diff = f"File: {change['new_path']}"
            diff += f"Diff:\n{change['diff']}"
            answer += "\n\n\n" + run_rag_query(diff)

        return answer

    else:
        print(f"Failed to fetch MR changes. Status: {response.status_code}")
        return (response.text)

