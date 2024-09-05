from keyRsa import get_server_key

# Usage example
url = "193.93.89.68"
server_response = get_server_key(url)
print("Response from server:", server_response)