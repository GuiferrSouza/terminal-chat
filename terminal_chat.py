import argparse
import asyncio
import sys
from server.server import start_server
from client.client import start_client

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Secure Terminal Chat Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Start a server:
    python terminal_chat.py serve 0.0.0.0 5000 --password mypassword
  
  Connect as client:
    python terminal_chat.py connect localhost 5000 Alice mypassword
        """
    )
    subparsers = parser.add_subparsers(dest="cmd", help="Command to execute")
    serve_parser = subparsers.add_parser("serve", help="Start a chat server")
    serve_parser.add_argument("host", help="Host address to bind (e.g., 0.0.0.0 or localhost)")
    serve_parser.add_argument("port", type=int, help="Port number to listen on (1024-65535 recommended)")
    serve_parser.add_argument("--password", required=True, help="Password for room authentication")
    connect_parser = subparsers.add_parser("connect", help="Connect to a chat server")
    connect_parser.add_argument("host", help="Server host address")
    connect_parser.add_argument("port", type=int, help="Server port number")
    connect_parser.add_argument("username", help="Your display name in the chat")
    connect_parser.add_argument("password", help="Room password")
    return parser.parse_args()

def validate_args(args):
    if args.cmd in ("serve", "connect"):
        if not (1 <= args.port <= 65535):
            print(f"Error: Port must be between 1 and 65535, got {args.port}")
            sys.exit(1)
        
        if args.cmd == "serve":
            if len(args.password) < 4:
                print("Error: Password must be at least 4 characters long")
                sys.exit(1)
        
        elif args.cmd == "connect":
            if not args.username.strip():
                print("Error: Username cannot be empty")
                sys.exit(1)
            if len(args.username) > 50:
                print("Error: Username must be 50 characters or less")
                sys.exit(1)


def main():
    args = parse_arguments()

    if not args.cmd:
        print("Error: No command specified. Use 'serve' or 'connect'")
        print("Run with --help for more information")
        sys.exit(1)

    validate_args(args)

    try:
        if args.cmd == "serve":
            asyncio.run(start_server(args.host, args.port, args.password))
        elif args.cmd == "connect":
            asyncio.run(start_client(
                args.host,
                args.port,
                args.username,
                args.password
            ))
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()