# Proxy-API-Service 🚀

## Description ✨

Proxy-API-Service is a Python-based FastAPI application designed to scrape, filter, and verify public HTTP/SOCKS proxies from GitHub repositories. It provides an API for downloading raw and verified proxy lists, ensuring you have access to reliable and secure proxy IPs.

## Features 🌟
- **FastAPI Server**: Handles API requests efficiently.
- **GitHub Scraping Logic**: Searches for proxy-related files on GitHub.
- **Proxy Testing Module**: Validates proxies using HTTP/SOCKS support.
- **Background Collection Loop**: Automatically updates proxy lists every 30 minutes.
- **Secure Authentication**: Protects download endpoints with basic authentication.

## Installation 🛠️

To install the required dependencies, run:

```bash
pip install -r requirements.txt
```

## Usage 📦

#### Download Proxy Lists

1. Start the FastAPI server:
    ```bash
    uvicorn main:app --reload
    ```

2. Access the download endpoint using a web browser or tool like `curl`:
    ```
    curl -u username:password http://localhost:8000/download/raw.txt
    ```

#### Example Code Snippet

```python
# Import necessary libraries
from fastapi import FastAPI, HTTPException
import uvicorn

app = FastAPI()

@app.get("/download/{file_name}")
async def download_file(file_name: str):
    # Logic to check authentication and return the file
    if file_name not in ["raw.txt", "proxies.txt"]:
        raise HTTPException(status_code=404, detail="File not found")
    
    with open(f"output/{file_name}", 'r') as file:
        content = file.read()
    
    return {"content": content}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## Configuration 🔧

- **Environment Variables**: Set the `GITHUB_TOKEN` environment variable to authenticate with GitHub.
- **Authentication**: Basic authentication is enabled for download endpoints.

## Proxy Testing Module 🛠️

The `utils/test_proxy.py` script tests a list of proxy servers for their validity:

```bash
python utils/test_proxy.py
```

This will output all the working proxies found in the text file and log the number of working proxies.

## Contributing 💻

Contributions are welcome! If you have any issues or suggestions, please open an issue on GitHub.

## License 📝

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

Built with ❤️ by [Your Name]