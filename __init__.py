import logging
import base64
import imghdr
from io import BytesIO
from PIL import Image
from PyPDF2 import PdfReader
import azure.functions as func

def convert_image_to_png(input_bytes):
    with Image.open(BytesIO(input_bytes)) as img:
        img = img.convert("RGBA")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return buffered.getvalue()

def convert_pdf_to_png(input_bytes):
    from pdf2image import convert_from_bytes
    images = convert_from_bytes(input_bytes)
    buffered = BytesIO()
    images[0].save(buffered, format="PNG")
    return buffered.getvalue()

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        file_b64 = body.get("file_base64")
        if not file_b64:
            return func.HttpResponse("Missing 'file_base64'", status_code=400)

        input_bytes = base64.b64decode(file_b64)
        file_type = imghdr.what(None, input_bytes)

        if file_type in ["jpeg", "jpg", "tiff"]:
            png_bytes = convert_image_to_png(input_bytes)
        elif input_bytes.startswith(b"%PDF"):
            png_bytes = convert_pdf_to_png(input_bytes)
        else:
            return func.HttpResponse("Unsupported file type", status_code=400)

        png_base64 = base64.b64encode(png_bytes).decode("utf-8")
        return func.HttpResponse(png_base64, status_code=200, mimetype="text/plain")

    except Exception as e:
        logging.exception("Conversion failed")
        return func.HttpResponse(f"Error: {str(e)}", status_code=500)