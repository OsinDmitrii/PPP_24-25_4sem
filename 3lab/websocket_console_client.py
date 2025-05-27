# websocket_console_client.py
"""
Интерактивный консольный клиент.

$ python websocket_console_client.py --user 1 --image path/to/picture.png
$ python websocket_console_client.py --user 1 --script commands.json
"""
import argparse
import asyncio
import base64
import json
import pathlib
import sys
from typing import Any

import websockets


def load_image(path: str | pathlib.Path) -> str:
    """Вспомогательная функция → base64 строки."""
    data = pathlib.Path(path).read_bytes()
    return base64.b64encode(data).decode()


async def producer(ws, initial_payload: dict[str, Any]) -> None:
    if initial_payload:
        await ws.send(json.dumps(initial_payload))
    #
    # while True:
    #     try:
    #         msg = input("Введите JSON-сообщение (или `exit`): ")
    #     except (EOFError, KeyboardInterrupt):
    #         break
    #     if msg.lower() in {"exit", "quit"}:
    #         break
    #     await ws.send(msg)


async def consumer(ws):
    async for message in ws:
        print(f"\n[WS] {message}")


async def main_async(args):
    uri = f"ws://{args.host}:{args.port}/ws/{args.user}"
    initial_payload = {}

    # режим «скрипт из файла»
    if args.script:
        initial_payload = json.loads(pathlib.Path(args.script).read_text())
    # режим «одно изображение»
    elif args.image:
        initial_payload = {
            "image": load_image(args.image),
            "algorithm": args.algorithm,
        }

    async with websockets.connect(uri) as ws:
        await asyncio.gather(consumer(ws), producer(ws, initial_payload))


def parse_args(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8000)
    p.add_argument("--user", type=int, required=True)
    p.add_argument("--image", help="Путь к изображению PNG/JPEG")
    p.add_argument("--algorithm", default="otsu")
    p.add_argument("--script", help="JSON-файл с готовыми командами")
    return p.parse_args(argv)


if __name__ == "__main__":
    asyncio.run(main_async(parse_args(sys.argv[1:])))
