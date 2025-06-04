import logging
import azure.functions as func
import base64
from io import BytesIO
from PIL import Image
import fitz  # PyMuPDF

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        req_body = req.get_json()
        file_data = base64.b64decode(req_body.get("file_base64", ""))
        img_format = req_body.get("format", "").lower()

        if not img_format or not file_data:
            return func.HttpResponse("Missing 'file_base64' or 'format'", status_code=400)

        # Konvertiere Bild oder PDF zu PNG
        if img_format in ["jpg", "jpeg", "tiff", "bmp"]:
            image = Image.open(BytesIO(file_data)).convert("RGB")
            buffer = BytesIO()
            image.save(buffer, format="PNG")
            result = base64.b64encode(buffer.getvalue()).decode()
        elif img_format == "pdf":
            doc = fitz.open(stream=file_data, filetype="pdf")
            page = doc.load_page(0)
            pix = page.get_pixmap()
            buffer = BytesIO(pix.tobytes("png"))
            result = base64.b64encode(buffer.getvalue()).decode()
        else:
            return func.HttpResponse(f"Unsupported format: {img_format}", status_code=400)

        return func.HttpResponse(result, status_code=200)

    except Exception as e:
        logging.exception("Error in convert_to_png")
        return func.HttpResponse(f"Internal Server Error: {str(e)}", status_code=500)