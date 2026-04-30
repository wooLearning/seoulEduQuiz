#!/usr/bin/env python3
"""Serve and open the RTL quiz HTML locally."""

from __future__ import annotations

import argparse
import functools
import os
import socket
import sys
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parent
HTML_FILE = "rtl_quiz_answers.html"
DATA_FILE = "rtl_quiz_data.json"


class QuietHandler(SimpleHTTPRequestHandler):
  def end_headers(self) -> None:
    self.send_header("Cache-Control", "no-store")
    super().end_headers()

  def log_message(self, fmt: str, *args: object) -> None:
    return


def find_free_port(preferred: int) -> int:
  for port in [preferred, *range(8766, 8810)]:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
      sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      try:
        sock.bind(("127.0.0.1", port))
      except OSError:
        continue
      return port
  raise RuntimeError("사용 가능한 로컬 포트를 찾지 못했습니다.")


def check_files() -> None:
  missing = [name for name in (HTML_FILE, DATA_FILE) if not (ROOT / name).exists()]
  if missing:
    names = ", ".join(missing)
    raise FileNotFoundError(f"필수 파일이 없습니다: {names}")


def main() -> int:
  parser = argparse.ArgumentParser(description="RTL quiz HTML viewer")
  parser.add_argument("--port", type=int, default=8765, help="preferred local port")
  parser.add_argument("--no-browser", action="store_true", help="print URL only")
  args = parser.parse_args()

  try:
    check_files()
    port = find_free_port(args.port)
  except Exception as exc:
    print(f"[ERROR] {exc}", file=sys.stderr)
    return 1

  os.chdir(ROOT)
  handler = functools.partial(QuietHandler, directory=str(ROOT))
  server = ThreadingHTTPServer(("127.0.0.1", port), handler)
  url = f"http://127.0.0.1:{port}/{HTML_FILE}"

  print("RTL quiz server is running.")
  print(f"URL: {url}")
  print("Stop: Ctrl+C")

  if not args.no_browser:
    webbrowser.open(url)

  try:
    server.serve_forever()
  except KeyboardInterrupt:
    print("\nServer stopped.")
  finally:
    server.server_close()

  return 0


if __name__ == "__main__":
  raise SystemExit(main())
