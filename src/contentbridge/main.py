import asyncio

from contentbridge.agents.discovery.discovery_agent import run_agent

def main() -> None:
    try:
        asyncio.run(run_agent())
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
