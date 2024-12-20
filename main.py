
import asyncio
import logging
from datetime import datetime
from typing import Dict, List
import cloudscraper
import requests

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO
)

class DawnValidatorBot:
    API_URLS = {
        "keepalive": "https://www.aeropres.in/chromeapi/dawn/v1/userreward/keepalive",
        "getPoints": "https://www.aeropres.in/api/atom/v1/userreferral/getpoint"
    }

    EXTENSION_ID = "fpdkjdnhkakefebpekbdhillbhonfjjp"
    VERSION = "1.1.1"

    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.scraper.proxies = {}

    def get_base_headers(self, token: str) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
            "Origin": "chrome-extension://fpdkjdnhkakefebpekbdhillbhonfjjp"
        }

    async def fetch_points(self, headers: Dict[str, str], appid: str) -> int:
        try:
            response = self.scraper.get(
                f"{self.API_URLS['getPoints']}?appid={appid}",
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            if data.get('status'):
                reward = data.get('data', {}).get('rewardPoint', {})
                referral = data.get('data', {}).get('referralPoint', {})
                return sum([
                    reward.get('points', 0),
                    referral.get('commission', 0)
                ])
        except Exception as e:
            logging.error(f"Failed to fetch points: {e}")
        return 0

    async def keep_alive_request(self, email: str, appid: str, token: str) -> bool:
        headers = self.get_base_headers(token)
        payload = {
            "username": email,
            "extensionid": self.EXTENSION_ID,
            "_v": self.VERSION
        }
        try:
            response = requests.post(
                f"{self.API_URLS['keepalive']}?appid={appid}",
                json=payload,
                headers=headers,
                proxies=self.scraper.proxies,
                timeout=30
            )
            response.raise_for_status()
            return True
        except Exception as e:
            logging.error(f"Keep-alive failed for {email}: {e}")
        return False

    async def process_account(self, account: Dict[str, str]) -> None:
        email = account['email']
        appid = account['appid']
        token = account['token']
        headers = self.get_base_headers(token)

        logging.info(f"Processing account: {email}")
        points = await self.fetch_points(headers, appid)
        logging.info(f"Current points for {email}: {points}")
        await self.keep_alive_request(email, appid, token)


def load_proxies(filename: str) -> Dict[str, str]:
    try:
        with open(filename, 'r') as f:
            proxy = f.readline().strip()
            return {"http": f"http://{proxy}", "https": f"http://{proxy}"}
    except FileNotFoundError:
        logging.error(f"Proxy file {filename} not found.")
        return {}

def load_accounts(filename: str) -> List[Dict[str, str]]:
    accounts = []
    try:
        with open(filename, 'r') as f:
            for line in f:
                email, token, appid = line.strip().split(',')
                accounts.append({"email": email, "token": token, "appid": appid})
    except FileNotFoundError:
        logging.error(f"Accounts file {filename} not found.")
    except ValueError:
        logging.error(f"Invalid account format in {filename}. Each line must have 'email,token,appid'.")
    return accounts


async def main():
    bot = DawnValidatorBot()
    logging.info("Dawn Validator Bot Initialized")

    bot.scraper.proxies.update(load_proxies('proxy.txt'))
    accounts = load_accounts('accounts.txt')

    if not accounts:
        logging.error("No accounts loaded. Exiting...")
        return

    try:
        while True:
            for account in accounts:
                await bot.process_account(account)
            await asyncio.sleep(60 * 5)
    except KeyboardInterrupt:
        logging.warning("Process interrupted by user. Exiting...")


if __name__ == "__main__":
    asyncio.run(main())