from PIL import Image

try:
	from pyzbar.pyzbar import decode as _pyzbar_decode

	def _decode_pil_image(image):
		return [item.data.decode("utf-8", errors="replace") for item in _pyzbar_decode(image)]

except ImportError:
	import zxingcpp  # type: ignore[import-untyped]

	def _decode_pil_image(image):
		return [r.text for r in zxingcpp.read_barcodes(image)]


def decode_qr_from_file(file_path):
	return _decode_pil_image(Image.open(file_path))


def decode_qr_from_pdf(pdf_path):
	import fitz  # pymupdf — imported lazily so missing package gives a clear ImportError

	results = []
	doc = fitz.open(pdf_path)  # type: ignore[attr-defined]
	for page_num, page in enumerate(doc, 1):  # type: ignore[arg-type]
		pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # type: ignore[attr-defined]
		img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
		results.append((page_num, _decode_pil_image(img)))
	return results
