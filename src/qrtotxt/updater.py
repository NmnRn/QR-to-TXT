import json
import threading
import urllib.request

CURRENT_VERSION = "1.3.0"
_REPO = "NmnRn/QR-to-TXT"


def check_for_update(on_found):
	"""Checks GitHub releases in a daemon thread. Calls on_found(version) if newer exists."""
	def _run():
		try:
			url = f"https://api.github.com/repos/{_REPO}/releases/latest"
			req = urllib.request.Request(url, headers={"User-Agent": "QRtoTXT-updater"})
			with urllib.request.urlopen(req, timeout=6) as resp:
				data = json.loads(resp.read())
			tag = data.get("tag_name", "").lstrip("v")
			if tag and _is_newer(tag, CURRENT_VERSION):
				on_found(tag)
		except Exception:
			pass

	threading.Thread(target=_run, daemon=True).start()


def _is_newer(a: str, b: str) -> bool:
	try:
		return tuple(int(x) for x in a.split(".")) > tuple(int(x) for x in b.split("."))
	except ValueError:
		return False
