import requests
import os
import base64
from dotenv import load_dotenv
from urllib.parse import urlparse, urljoin

# Set to GitHub's API base URL
load_dotenv()
GITHUB_API_URL = 'https://api.github.com/'
#print(os.getenv('GITACC_TOKEN'))
def parse_github_repo_url(repo_url):
    """
    Parses a GitHub repository URL and extracts the owner and repository name.
    """
    path_parts = urlparse(repo_url).path.strip('/').split('/')
    if len(path_parts) >= 2:
        return path_parts[0], path_parts[1]
    else:
        raise ValueError("Invalid GitHub repository URL.")

def get_files_from_repo(repo_url, token, extensions):
    """
    Fetches files from a GitHub repository with specific extensions.
    """
    owner, repo = parse_github_repo_url(repo_url)
    api_url = f"repos/{owner}/{repo}/git/trees/main?recursive=1"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(urljoin(GITHUB_API_URL, api_url), headers=headers)
    response.raise_for_status()

    tree = response.json()['tree']
    download_urls = [
        item['path'] for item in tree
        if item['type'] == 'blob' and any(item['path'].endswith(ext) for ext in extensions)
    ]

    return download_urls

def get_file_content(owner, repo, file_path, token):
    """
    Fetches the content of a file from the GitHub repository.
    """
    api_url = f"repos/{owner}/{repo}/contents/{file_path}"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(urljoin(GITHUB_API_URL, api_url), headers=headers)
    response.raise_for_status()

    content_data = response.json()
    if content_data.get('encoding') == 'base64':
        content = base64.b64decode(content_data['content']).decode('utf-8')
    else:
        content = content_data['content']
    return content
def write_content_to_file(file_path, content):
    """
    Writes the content of a GitHub file to a local file with the same extension.

    :param file_path: Path of the file on GitHub
    :param content: Content of the file to write
    """
    # Create directories if they don't exist
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Write the content to a file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    print(f"File written: {file_path}")

# # Add this to the loop where you process and possibly summarize the content
# for file_path in file_paths:
#     content = get_file_content(owner, repo, file_path, token)
#     # Call the function to write content to file
#     local_file_path = os.path.join("./codes", file_path)  # Replace 'local_directory' with your desired local path
#     write_content_to_file(local_file_path, content)


# Example usage:

def downloadRepo(repo_url):
    extensions = ('.cpp','.h','.py','.java','.txt','.md')
    token = os.getenv('GITACC_TOKEN') # Replace with your GitHub token

    try:
        owner, repo = parse_github_repo_url(repo_url)
        file_paths = get_files_from_repo(repo_url, token, extensions)
        for file_path in file_paths:
            content = get_file_content(owner, repo, file_path, token)
            # Call the function to write content to file
            local_file_path = os.path.join("./codes", file_path)  # Replace 'local_directory' with your desired local path
            write_content_to_file(local_file_path, content)
            # Here, you would process and possibly summarize the content
            #print(content)  # Replace with processing logic
    except requests.HTTPError as e:
        print(f"HTTP Error: {e.response.json()}")
    except Exception as e:
        print(f"An error occurred: {e}")
