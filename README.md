
# Dawn Validator Bot

## Description
This script automates account validation on a specific platform. It uses proxies and accounts loaded from external files.

## Installation

1. **Clone the repository or copy the script to your directory.**
2. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **File `proxy.txt`**  
   Add one proxy per line in the following format:  
   ```
   username:password@proxyhost:port
   ```

2. **File `accounts.txt`**  
   Add accounts in the following format (one account per line):  
   ```
   email,token,appid
   ```

## Running the Script

Run the script with the command:
```bash
python main.py
```

The program will process the accounts, send keep-alive requests, and fetch points periodically.

## Notes
- Ensure `proxy.txt` and `accounts.txt` are in the same directory as the script.
- Use `Ctrl+C` to stop the program manually.