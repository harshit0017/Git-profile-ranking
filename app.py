import streamlit as st 
import pandas as pd
import openai
import os
from dotenv import load_dotenv
import pandas as pd
import json
import requests
import re
from collections import Counter
load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')

def fetch_user_repositories(user_url):
    username = user_url.split('/')[-1]  # Extract the username from the URL
    response = requests.get(f'https://api.github.com/users/{username}/repos', headers={'Authorization': f'token {GITHUB_TOKEN}'})
    print(f"ye rha {response}")
    if response.status_code == 200:
        return response.json()
    else:
        print("Error response from GitHub API:", response.text)
        return []
def generate_repo_report(repository_data):
    repo_report = {}
    
    for repo in repository_data:
        repo_id = repo['id']
        owner_login = repo['owner']['login']
        repo_name = repo['name']
        repo_link = f"https://github.com/{owner_login}/{repo_name}"  # Constructing the repository link
        description = repo['description']
        language = repo['language']
        size = repo['size']
        stargazers_count = repo['stargazers_count']
        watchers_count = repo['watchers_count']
        forks_count = repo['forks_count']
        open_issues_count = repo['open_issues_count']
            
        
        # # Additional attributes that might indicate complexity
        commits_count = get_commits_count(repo_name, owner_login)  # Replace with actual function to get commits count
        contributors_count = get_contributors_count(repo_name, owner_login)  # Replace with actual function to get contributors count
        # libraries_used = get_libraries_used(repo_name, owner_login) 
        lines_of_code = get_lines_of_code(repo_name, owner_login)
        # Create a dictionary with relevant information for the repository
        repo_info = {
                        "name": repo_name,
                        "language": language,
                        "size": size,
                        "stargazers_count": stargazers_count,
                        "watchers_count": watchers_count,
                        "forks_count": forks_count,
                        "open_issues_count": open_issues_count,
                        "commits_count": commits_count,
                        "contributors_count": contributors_count,
                        "lines_of_code": lines_of_code
                    }

        
        # Store the repository information in the report dictionary
        repo_report[repo_link] = repo_info
    
    return repo_report   
def get_commits_count(repo_name, owner):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/commits"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        commits = response.json()
        return len(commits)
    else:
        return 0

def get_contributors_count(repo_name, owner):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/contributors"
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        contributors = response.json()
        return len(contributors)
    else:
        return 0
import requests

def get_lines_of_code(repo_name, owner):
    url = f"https://api.github.com/repos/{owner}/{repo_name}/stats/code_frequency"
    response = requests.get(url)
    
    if response.status_code == 200:
        code_frequency = response.json()
        
        total_lines_added = sum(entry[1] for entry in code_frequency)
        total_lines_deleted = sum(entry[2] for entry in code_frequency)
        
        # Calculate total lines of code by adding lines added and subtracting lines deleted
        total_lines_of_code = total_lines_added + total_lines_deleted
        
        return total_lines_of_code
    else:
        return 300

 
st.title(" github repo extraction")
url= st.text_input("enter the github profile")
profile= fetch_user_repositories(url)
#st.write(profile)
print(profile)
report = generate_repo_report(profile)
st.write(report)
def calculate_complexity_score(repo_details):
    lines_of_code = repo_details.get("lines_of_code", 0)
    contributors_count = repo_details.get("contributors_count", 0)
    open_issues_count = repo_details.get("open_issues_count", 0)
    commits_count = repo_details.get("commits_count", 0)
    stargazers_count = repo_details.get("stargazers_count", 0)
    watchers_count = repo_details.get("watchers_count", 0)
    forks_count = repo_details.get("forks_count", 0)

    normalized_lines_of_code = max(0, lines_of_code / 100)
    normalized_contributors_count = max(0, contributors_count / 100)
    normalized_open_issues_count = max(0, open_issues_count / 100)
    normalized_commits_count = max(0, commits_count / 1000)
    normalized_stargazers_count = max(0, stargazers_count / 1000)
    normalized_watchers_count = max(0, watchers_count / 1000)
    normalized_forks_count = max(0, forks_count / 100)

    # Use the adjusted normalized values to calculate the weighted complexity score
    weighted_complexity_score = (
        20 * normalized_lines_of_code +
        10 * normalized_contributors_count +
        10 * normalized_open_issues_count +
        15 * normalized_commits_count +
        15 * normalized_stargazers_count +
        15 * normalized_watchers_count +
        15 * normalized_forks_count
    )

    # Scale the weighted complexity score to be between 1 and 100
    complexity_score = weighted_complexity_score 

    return min(100,complexity_score)
  # Ensure the score is between 1 and 100
for repo_link, repo_details in report.items():
    complexity_score = calculate_complexity_score(repo_details)
    # st.write(f"Repository: {repo_link}, Complexity Score: {complexity_score}")



# Calculate and store individual complexity scores
complexity_scores = []
for repo_link, repo_details in report.items():
    complexity_score = calculate_complexity_score(repo_details)
    complexity_scores.append(complexity_score)
    st.write(f"Repository: {repo_link}, Complexity Score: {complexity_score}")

# Calculate and display the overall complexity score
if complexity_scores:
    overall_complexity = sum(complexity_scores) / len(complexity_scores)
    st.write(f"Overall Profile Score for User  {overall_complexity}")
else:
    st.write("No repositories found for the user.")
