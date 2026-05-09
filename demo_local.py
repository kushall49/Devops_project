"""
🖼️  Serverless Image Processing - LOCAL DEMO
==============================================
This demo runs the complete image processing pipeline locally without Docker,
allowing you to see what the serverless functions do in real-time!

Features:
- Image Resize: Scale images to any dimension
- Image Enhance: Adjust brightness, contrast, sharpness, color saturation
- Image Filter: Apply 13+ artistic and transformative filters
- Pipeline: Chain operations (resize → enhance → filter)
"""

import base64
import io
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
import uvicorn

# ============================================================================
# IMAGE PROCESSING FUNCTIONS
# ============================================================================

class ImageProcessor:
    """Local image processing without MinIO or OpenFaaS"""

    @staticmethod
    def resize(
        image_bytes: bytes,
        width: Optional[int] = None,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = False,
        fmt: str = "JPEG",
        quality: int = 85,
    ) -> bytes:
        """Resize image to specified dimensions"""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        orig_w, orig_h = img.size

        if maintain_aspect_ratio:
            if width and not height:
                ratio = width / orig_w
                height = int(orig_h * ratio)
            elif height and not width:
                ratio = height / orig_h
                width = int(orig_w * ratio)
            elif width and height:
                ratio = min(width / orig_w, height / orig_h)
                width = int(orig_w * ratio)
                height = int(orig_h * ratio)
            else:
                width, height = orig_w, orig_h
        else:
            width = width or orig_w
            height = height or orig_h

        img = img.resize((width, height), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format=fmt, quality=quality)
        return buf.getvalue()

    @staticmethod
    def enhance(
        image_bytes: bytes,
        brightness: float = 1.0,
        contrast: float = 1.0,
        sharpness: float = 1.0,
        color: float = 1.0,
        auto_equalize: bool = False,
    ) -> bytes:
        """Enhance image properties"""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        img = ImageEnhance.Brightness(img).enhance(brightness)
        img = ImageEnhance.Contrast(img).enhance(contrast)
        img = ImageEnhance.Sharpness(img).enhance(sharpness)
        img = ImageEnhance.Color(img).enhance(color)

        if auto_equalize:
            img = ImageOps.equalize(img)

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue()

    @staticmethod
    def filter(image_bytes: bytes, filter_name: str = "grayscale") -> bytes:
        """Apply artistic filters"""
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        name = filter_name.lower()

        if name == "grayscale":
            img = img.convert("L").convert("RGB")
        elif name == "blur":
            img = img.filter(ImageFilter.BLUR)
        elif name == "blur_heavy":
            img = img.filter(ImageFilter.GaussianBlur(radius=5))
        elif name == "sharpen":
            img = img.filter(ImageFilter.SHARPEN)
        elif name == "edge":
            gray = img.convert("L")
            edges = gray.filter(ImageFilter.FIND_EDGES)
            img = edges.convert("RGB")
        elif name == "emboss":
            img = img.filter(ImageFilter.EMBOSS)
        elif name == "smooth":
            img = img.filter(ImageFilter.SMOOTH_MORE)
        elif name == "detail":
            img = img.filter(ImageFilter.DETAIL)
        elif name == "contour":
            img = img.filter(ImageFilter.CONTOUR)
        elif name == "sepia":
            grayscale = img.convert("L").convert("RGB")
            r, g, b = grayscale.split()
            r = r.point(lambda i: min(255, int(i * 1.08)))
            g = g.point(lambda i: min(255, int(i * 0.87)))
            b = b.point(lambda i: min(255, int(i * 0.69)))
            img = Image.merge("RGB", (r, g, b))
        elif name == "invert":
            img = ImageOps.invert(img)
        elif name == "posterize":
            img = ImageOps.posterize(img, bits=3)
        elif name == "solarize":
            img = ImageOps.solarize(img, threshold=128)
        else:
            raise ValueError(f"Unknown filter: '{filter_name}'")

        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return buf.getvalue()


def create_demo_image(width: int = 400, height: int = 300) -> bytes:
    """Create a colorful test image with gradient and shapes"""
    img = Image.new("RGB", (width, height))
    pixels = img.load()

    # Create gradient background
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255)
            g = int((y / height) * 255)
            b = 128
            pixels[x, y] = (r, g, b)

    # Draw shapes
    draw = Image.new("RGB", (width, height))
    draw.paste(img)

    # Add text overlay
    from PIL import ImageDraw
    d = ImageDraw.Draw(draw)
    d.rectangle([50, 50, 150, 150], fill="red", outline="white", width=3)
    d.ellipse([200, 100, 300, 200], fill="green", outline="white", width=3)
    d.polygon([(100, 250), (150, 200), (200, 250)], fill="yellow", outline="white")

    buf = io.BytesIO()
    draw.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


# ============================================================================
# FASTAPI APPLICATION
# ============================================================================

app = FastAPI(
    title="🖼️  Image Processing Pipeline (LOCAL DEMO)",
    description="See serverless image processing in action - no Docker required!",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", summary="Welcome")
def welcome():
    """Welcome to the demo"""
    return {
        "app": "Serverless Image Processing Pipeline - LOCAL DEMO",
        "message": "Upload an image or try a test image at /docs",
        "endpoints": [
            {"method": "GET", "path": "/demo-image", "description": "Download test image"},
            {"method": "POST", "path": "/process/resize", "description": "Resize image"},
            {"method": "POST", "path": "/process/enhance", "description": "Enhance image"},
            {"method": "POST", "path": "/process/filter", "description": "Apply filter"},
            {"method": "POST", "path": "/process/pipeline", "description": "Run complete pipeline"},
            {"method": "GET", "path": "/docs", "description": "Interactive API documentation"},
        ],
    }


@app.get("/demo-image", summary="Download a test image")
def get_demo_image():
    """Get a colorful test image to process"""
    img_bytes = create_demo_image()
    return StreamingResponse(
        io.BytesIO(img_bytes),
        media_type="image/jpeg",
        headers={"Content-Disposition": "attachment; filename=demo-image.jpg"}
    )


@app.post("/process/resize", summary="Resize image")
async def resize_image(
    file: UploadFile = File(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    maintain_aspect_ratio: bool = Form(False),
    quality: int = Form(85),
):
    """
    Resize image to specified dimensions
    
    **Parameters:**
    - `width`: Target width (optional)
    - `height`: Target height (optional)
    - `maintain_aspect_ratio`: Keep aspect ratio (default: false)
    - `quality`: JPEG quality 1-95 (default: 85)
    """
    try:
        image_bytes = await file.read()
        result = ImageProcessor.resize(
            image_bytes,
            width=width,
            height=height,
            maintain_aspect_ratio=maintain_aspect_ratio,
            quality=quality,
        )
        return StreamingResponse(
            io.BytesIO(result),
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=resized.jpg"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Resize error: {str(e)}")


@app.post("/process/enhance", summary="Enhance image")
async def enhance_image(
    file: UploadFile = File(...),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    sharpness: float = Form(1.0),
    color: float = Form(1.0),
    auto_equalize: bool = Form(False),
):
    """
    Enhance image properties
    
    **Parameters:**
    - `brightness`: 0.5-2.0 (1.0 = normal)
    - `contrast`: 0.5-2.0 (1.0 = normal)
    - `sharpness`: 0.0-2.0 (1.0 = normal)
    - `color`: 0.0-2.0 (0 = grayscale, 1.0 = normal)
    - `auto_equalize`: Apply histogram equalization
    """
    try:
        image_bytes = await file.read()
        result = ImageProcessor.enhance(
            image_bytes,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            color=color,
            auto_equalize=auto_equalize,
        )
        return StreamingResponse(
            io.BytesIO(result),
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=enhanced.jpg"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Enhance error: {str(e)}")


@app.post("/process/filter", summary="Apply filter")
async def apply_filter(
    file: UploadFile = File(...),
    filter: str = Form("grayscale"),
):
    """
    Apply artistic filter to image
    
    **Available filters:**
    - grayscale, blur, blur_heavy, sharpen, edge, emboss
    - smooth, detail, contour, sepia, invert, posterize, solarize
    """
    try:
        image_bytes = await file.read()
        result = ImageProcessor.filter(image_bytes, filter_name=filter)
        return StreamingResponse(
            io.BytesIO(result),
            media_type="image/jpeg",
            headers={"Content-Disposition": f"attachment; filename=filtered-{filter}.jpg"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Filter error: {str(e)}")


@app.post("/process/pipeline", summary="Complete pipeline (resize → enhance → filter)")
async def pipeline(
    file: UploadFile = File(...),
    width: Optional[int] = Form(None),
    height: Optional[int] = Form(None),
    brightness: float = Form(1.0),
    contrast: float = Form(1.0),
    sharpness: float = Form(1.0),
    color: float = Form(1.0),
    filter: str = Form("grayscale"),
):
    """
    Run complete pipeline: Resize → Enhance → Apply Filter
    
    Combines all three processing steps in sequence.
    """
    try:
        image_bytes = await file.read()

        # Step 1: Resize
        image_bytes = ImageProcessor.resize(
            image_bytes,
            width=width,
            height=height,
            maintain_aspect_ratio=True,
        )

        # Step 2: Enhance
        image_bytes = ImageProcessor.enhance(
            image_bytes,
            brightness=brightness,
            contrast=contrast,
            sharpness=sharpness,
            color=color,
        )

        # Step 3: Filter
        image_bytes = ImageProcessor.filter(image_bytes, filter_name=filter)

        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type="image/jpeg",
            headers={"Content-Disposition": "attachment; filename=pipeline-result.jpg"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Pipeline error: {str(e)}")


@app.get("/health", summary="Health check")
def health():
    """Check service health"""
    return {
        "status": "🟢 healthy",
        "service": "Image Processing Pipeline (LOCAL)",
        "mode": "Demo (no containers required)",
    }


@app.get("/functions", summary="Available functions")
def list_functions():
    """List all available functions"""
    return {
        "available": [
            {
                "name": "resize",
                "description": "Scale images to custom dimensions",
                "filters": ["width", "height", "maintain_aspect_ratio", "quality"],
            },
            {
                "name": "enhance",
                "description": "Adjust brightness, contrast, sharpness, saturation",
                "filters": ["brightness", "contrast", "sharpness", "color", "auto_equalize"],
            },
            {
                "name": "filter",
                "description": "Apply artistic/transformative filters",
                "filters": [
                    "grayscale", "blur", "blur_heavy", "sharpen", "edge",
                    "emboss", "smooth", "detail", "contour", "sepia",
                    "invert", "posterize", "solarize"
                ],
            },
            {
                "name": "pipeline",
                "description": "Chain: resize → enhance → filter",
                "filters": "All filters from resize, enhance, and filter combined",
            },
        ],
        "demo_features": [
            "✅ No Docker required",
            "✅ No OpenFaaS required",
            "✅ All processing happens locally",
            "✅ Interactive API docs at /docs",
            "✅ Download test image at /demo-image",
        ],
    }


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🚀  SERVERLESS IMAGE PROCESSING - LOCAL DEMO")
    print("=" * 70)
    print("\n📋 Features:")
    print("   ✅ Image Resize - Scale to any dimension")
    print("   ✅ Image Enhance - Adjust brightness, contrast, sharpness, color")
    print("   ✅ Image Filter - Apply 13+ artistic filters")
    print("   ✅ Pipeline - Chain operations together")
    print("\n🌐 API Endpoints:")
    print("   📍 GET  http://localhost:5000/           - Welcome")
    print("   📍 GET  http://localhost:5000/demo-image - Download test image")
    print("   📍 POST http://localhost:5000/process/resize   - Resize")
    print("   📍 POST http://localhost:5000/process/enhance  - Enhance")
    print("   📍 POST http://localhost:5000/process/filter   - Apply filter")
    print("   📍 POST http://localhost:5000/process/pipeline - Complete pipeline")
    print("\n📚 Interactive Docs:")
    print("   📖 http://localhost:5000/docs     - Swagger UI (try it out!)")
    print("   📖 http://localhost:5000/redoc    - ReDoc")
    print("\n⚙️  Starting server...")
    print("=" * 70 + "\n")

    uvicorn.run(app, host="0.0.0.0", port=5000)
