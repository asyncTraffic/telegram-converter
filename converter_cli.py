import os, asyncio, argparse, sys, re
from pathlib import Path
from PyQt6.QtCore import QSettings
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from opentele.td import TDesktop
from opentele.api import UseCurrentSession
from loguru import logger

logger.remove()
logger.add(
    "converter.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    filter=lambda record: "sensitive" not in record["extra"],
    backtrace=True,
    diagnose=True
)
logger.add(
    sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    level="INFO",
    filter=lambda record: "sensitive" not in record["extra"],
    backtrace=True,
    diagnose=True
)

async def session_to_tdata(session_path, api_id, api_hash, proxy_data=None, output_dir=None):
    if not os.path.exists(session_path):
        logger.error(f"Session file not found: {session_path}")
        raise FileNotFoundError("The selected .session file was not found. Please check the file path.")

    if output_dir is None:
        output_dir = os.path.dirname(session_path)
    
    session_name = os.path.splitext(os.path.basename(session_path))[0]
    tdata_dir = os.path.join(output_dir, f"{session_name}_tdata")

    proxy = None
    if proxy_data and proxy_data.get('ip') and proxy_data.get('port') and proxy_data.get('type'):
        proxy = (
            proxy_data['type'],
            proxy_data['ip'],
            int(proxy_data['port']),
            True,
            proxy_data.get('login'),
            proxy_data.get('password')
        )
        logger.info(f"Using proxy type: {proxy_data['type']}")
    else:
        logger.info("No proxy configured")

    try:
        client = TelegramClient(
            session_path,
            api_id=int(api_id),
            api_hash=api_hash,
            proxy=proxy if proxy else None
        )
    except Exception as e:
        logger.warning(f"Failed to initialize TelegramClient with session file: {str(e)}")
        try:
            with open(session_path, "r") as f:
                session_string = f.read().strip()
            logger.info("Session string loaded from session file")
            client = TelegramClient(
                StringSession(session_string),
                api_id=int(api_id),
                api_hash=api_hash,
                proxy=proxy if proxy else None
            )
        except Exception as e:
            logger.exception(f"Failed to read session file or initialize client")
            raise ValueError("Unable to initialize Telegram session. Please check the session file or API credentials.")

    try:
        tdesk = await client.ToTDesktop(flag=UseCurrentSession)
        tdesk.SaveTData(os.path.join(tdata_dir, "tdata"))
        logger.info(f"tdata saved to: {tdata_dir}")
        return tdata_dir
    except Exception as e:
        logger.exception(f"Conversion to tdata failed")
        raise RuntimeError("Failed to convert session to tdata. Please try again or check the logs.")

def parse_proxy_string(proxy_string, proxy_type):
    if not proxy_string:
        return None

    pattern = r"^(?:(?P<login>[^:]+):(?P<password>[^@]+)@)?(?P<ip>[^:]+):(?P<port>\d+)$"
    match = re.match(pattern, proxy_string)
    if not match:
        logger.error("Invalid proxy format provided")
        raise ValueError("Please enter proxy in format login:password@ip:port or ip:port")

    return {
        'type': proxy_type,
        'ip': match.group('ip'),
        'port': match.group('port'),
        'login': match.group('login'),
        'password': match.group('password')
    }

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
        help="Telegram API ID"
    )
    parser.add_argument(
        "--api-hash",
        help="Telegram API Hash"
    )
    parser.add_argument(
        "--proxy-type",
        choices=["http", "https", "socks5", "socks4"],
        help="Proxy type (http, https, socks5, socks4)"
    )
    parser.add_argument(
        "--proxy",
        help="Proxy in format login:password@ip:port or ip:port"
    )

    args = parser.parse_args()

    if args.proxy_type and not args.proxy:
        print("Error: --proxy is required when --proxy-type is provided")
        sys.exit(1)
    if args.proxy and not args.proxy_type:
        print("Error: --proxy-type is required when --proxy is provided")
        sys.exit(1)

    settings = QSettings("AsyncTraffic", "Converter")
    api_id = args.api_id or settings.value("api_id", "")
    api_hash = args.api_hash or settings.value("api_hash", "")

    if not api_id or not api_hash:
        print("Error: --api-id and --api-hash are required for the first run or if not saved")
        sys.exit(1)

    settings.setValue("api_id", api_id)
    settings.setValue("api_hash", api_hash)

    data_dir = os.path.join(os.getcwd(), "data")
    os.makedirs(data_dir, exist_ok=True)

    proxy_data = None
    if args.proxy_type and args.proxy:
        try:
            proxy_data = parse_proxy_string(args.proxy, args.proxy_type)
        except ValueError as e:
            print(f"Error: {str(e)}")
            sys.exit(1)

    try:
        loop = asyncio.get_event_loop()
        tdata_dir = loop.run_until_complete(
            session_to_tdata(
                session_path=args.session,
                api_id=api_id,
                api_hash=api_hash,
                proxy_data=proxy_data,
                output_dir=data_dir
            )
        )
        print(f"Success: tdata saved to {tdata_dir}")
    except FileNotFoundError as e:
        logger.exception("Session file error")
        print(f"Error: {str(e)}")
        sys.exit(1)
    except ValueError as e:
        logger.exception("Session initialization error")
        print(f"Error: {str(e)}")
        sys.exit(1)
    except RuntimeError as e:
        logger.exception("Conversion error")
        print(f"Error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        logger.exception("Unexpected error during conversion")
        print("Error: An unexpected error occurred. Please check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
