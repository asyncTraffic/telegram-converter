import os, sys, asyncio, argparse
from pathlib import Path
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from opentele.td import TDesktop
from opentele.api import UseCurrentSession
from loguru import logger

async def session_to_tdata(session_path, api_id, api_hash, proxy_data=None, output_dir=None):

    if not os.path.exists(session_path):
        raise FileNotFoundError(f"Session file {session_path} not found")

    if output_dir is None:
        output_dir = os.path.dirname(session_path)

    session_name = os.path.splitext(os.path.basename(session_path))[0]
    tdata_dir = os.path.join(output_dir, f"{session_name}_tdata")

    proxy = None
    if proxy_data and proxy_data.get('ip') and proxy_data.get('port'):
        proxy = (
            'socks5',
            proxy_data['ip'],
            int(proxy_data['port']),
            True,
            proxy_data.get('login'),
            proxy_data.get('password')
        )

    try:
        client = TelegramClient(
            session_path,
            api_id=int(api_id),
            api_hash=api_hash,
            proxy=proxy if proxy else None
        )
    except Exception as e:
        logger.warning(e)

        try:
            with open(session_path, "r") as f:
                session_string = f.read().strip()
            logger.info("Session string loaded from session.session")
        except Exception as e:
            logger.error(f"Failed to read session file: {e}")
            return

        client = TelegramClient(StringSession(session_string), api_id=int(api_id), api_hash=api_hash, proxy=proxy if proxy else None)
        
    tdesk = await client.ToTDesktop(flag=UseCurrentSession)
    tdesk.SaveTData(os.path.join(tdata_dir, "tdata"))
    
    return tdata_dir

def main():
    parser = argparse.ArgumentParser(
        description="AsyncTraffic Converter CLI: Convert .session file to tdata"
    )
    parser.add_argument(
        "--session",
        required=True,
        help="Path to the .session file"
    )
    parser.add_argument(
        "--api-id",
        required=True,
        type=int,
        help="Telegram API ID"
    )
    parser.add_argument(
        "--api-hash",
        required=True,
        help="Telegram API Hash"
    )
    parser.add_argument(
        "--proxy-ip",
        help="Proxy IP address (optional)"
    )
    parser.add_argument(
        "--proxy-port",
        type=int,
        help="Proxy port (required if proxy-ip is provided)"
    )
    parser.add_argument(
        "--proxy-login",
        help="Proxy login (optional)"
    )
    parser.add_argument(
        "--proxy-password",
        help="Proxy password (optional)"
    )

    args = parser.parse_args()

    proxy_data = None
    if args.proxy_ip:
        if not args.proxy_port:
            print("Error: --proxy-port is required when --proxy-ip is provided")
            sys.exit(1)
        proxy_data = {
            'ip': args.proxy_ip,
            'port': args.proxy_port,
            'login': args.proxy_login,
            'password': args.proxy_password
        }

    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)

    try:
        loop = asyncio.get_event_loop()
        tdata_dir = loop.run_until_complete(
            session_to_tdata(
                session_path=args.session,
                api_id=args.api_id,
                api_hash=args.api_hash,
                proxy_data=proxy_data,
                output_dir=data_dir
            )
        )
        print(tdata_dir)
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()