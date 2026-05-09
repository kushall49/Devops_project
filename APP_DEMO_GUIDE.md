# 🖼️ SERVERLESS IMAGE PROCESSING - DEMO APP

## ✅ APP IS NOW RUNNING!

**Server Status:** 🟢 **ACTIVE** at `http://localhost:5000`

---

## 📋 What This App Does

This is a **serverless image processing pipeline** that allows you to:

### 1. **Image Resizing** 📐
- Scale images to any width/height
- Maintain aspect ratio automatically
- Adjust JPEG quality (1-95)
- Preserve or convert image formats

### 2. **Image Enhancement** ✨
- **Brightness**: 0.5-2.0 (1.0 = normal)
- **Contrast**: 0.5-2.0 (higher = more dramatic)
- **Sharpness**: 0.0-2.0 (enhance details)
- **Color/Saturation**: 0.0-2.0 (0 = grayscale, 2 = super vibrant)
- **Auto-Equalize**: Apply histogram equalization for better contrast

### 3. **Artistic Filters** 🎨
13+ filters available:
- **Grayscale** - Convert to black & white
- **Blur** - Soft blur effect
- **Blur Heavy** - Stronger blur (Gaussian)
- **Sharpen** - Enhance edges
- **Edge** - Extract edges only
- **Emboss** - 3D effect
- **Smooth** - Remove noise
- **Detail** - Enhance fine details
- **Contour** - Highlight outlines
- **Sepia** - Vintage brown tone
- **Invert** - Negative effect
- **Posterize** - Reduce colors (comic effect)
- **Solarize** - High-contrast artistic effect

### 4. **Complete Pipeline** 🔄
Chain all operations: **Resize → Enhance → Filter**
- Process in sequence
- Get final result in one call

---

## 🌐 API Endpoints

### **Interactive Testing**
📖 **Swagger UI**: http://localhost:5000/docs (TRY LIVE!)

### **Available Endpoints**

| Method | Endpoint | Purpose |
|--------|----------|---------|
| **GET** | `/demo-image` | Download a colorful test image |
| **POST** | `/process/resize` | Resize image |
| **POST** | `/process/enhance` | Enhance brightness/contrast/etc |
| **POST** | `/process/filter` | Apply artistic filters |
| **POST** | `/process/pipeline` | Resize → Enhance → Filter |
| **GET** | `/health` | Health check |
| **GET** | `/functions` | List available functions |

---

## 🧪 How to Test

### **Option 1: Interactive Web UI (Recommended)**
1. Open: http://localhost:5000/docs
2. Click any endpoint to expand it
3. Click "Try it out"
4. For file uploads: Click "Choose File" to select an image
5. For filters: Set parameters (e.g., `filter=sepia`)
6. Click "Execute"
7. See the result immediately!

### **Option 2: Download Test Image & Process It**
```bash
# 1. Download demo image
curl http://localhost:5000/demo-image > test.jpg

# 2. Resize it
curl -X POST -F "file=@test.jpg" \
  -F "width=200" \
  -F "height=200" \
  -F "maintain_aspect_ratio=true" \
  http://localhost:5000/process/resize > resized.jpg

# 3. Apply a sepia filter
curl -X POST -F "file=@test.jpg" \
  -F "filter=sepia" \
  http://localhost:5000/process/filter > sepia.jpg

# 4. Run full pipeline
curl -X POST -F "file=@test.jpg" \
  -F "width=400" \
  -F "brightness=1.2" \
  -F "contrast=1.1" \
  -F "sharpness=1.3" \
  -F "filter=sepia" \
  http://localhost:5000/process/pipeline > result.jpg
```

---

## 🎯 Example Workflows

### **Workflow 1: Resize & Make Grayscale**
1. Upload image
2. Resize to 300x300 with aspect ratio
3. Apply "grayscale" filter
→ Result: Thumbnail-sized B&W image

### **Workflow 2: Enhance for Social Media**
1. Upload image
2. Brightness: 1.1 (slightly brighter)
3. Contrast: 1.2 (more pop)
4. Color: 1.3 (vibrant)
5. Filter: none (keep color)
→ Result: Eye-catching image for social posts

### **Workflow 3: Create Vintage Look**
1. Upload image
2. Reduce saturation (color: 0.7)
3. Apply sepia filter
4. Add slight blur for softness
→ Result: Nostalgic vintage photograph

### **Workflow 4: Create Artistic Effect**
1. Upload image
2. Apply "edge" filter to detect edges
3. Apply "emboss" for 3D effect
4. Apply "posterize" for comic look
→ Result: Artistic transformations

---

## 💻 Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI (Python) |
| **Server** | Uvicorn |
| **Image Processing** | Pillow (PIL) |
| **API Docs** | Swagger UI / OpenAPI |

### **Why No Docker?**
This demo runs **locally on Windows** without Docker:
- No containers needed
- No OpenFaaS required
- Direct Python execution
- All processing happens instantly
- Perfect for testing and understanding the pipeline

---

## 🚀 Real Production Setup

The full project includes:
- **OpenFaaS (faasd)** - Serverless runtime for actual functions
- **MinIO** - S3-compatible object storage
- **Prometheus + Grafana** - Monitoring & metrics
- **Docker Compose** - Orchestration
- **Event-Driven Webhooks** - MinIO triggers functions automatically

**To run the full stack with containers:**
```bash
cd ~/serverless-image-processing
docker-compose up -d
bash scripts/setup.sh
```

---

## 📊 Architecture (This Demo vs Full Stack)

### **This Demo (LOCAL)**
```
Your File
    ↓
FastAPI Gateway
    ↓
Image Processor (Python)
    ↓
Processed Image
```

### **Full Stack (Production)**
```
MinIO Upload
    ↓
S3 Webhook Event
    ↓
fn-minio-trigger (OpenFaaS)
    ↓
Routes to appropriate function:
    ├─ fn-image-resize
    ├─ fn-image-enhance
    └─ fn-image-filter
    ↓
MinIO (processed/ bucket)
    ↓
Prometheus (metrics)
    ↓
Grafana (dashboards)
```

---

## 📝 Project Files Explained

### **Main Gateway**
- `gateway/app.py` - FastAPI REST API gateway

### **Serverless Functions**
- `fn-image-resize/handler.py` - Image resizing function
- `fn-image-enhance/handler.py` - Image enhancement function
- `fn-image-filter/handler.py` - Artistic filter function
- `fn-minio-trigger/handler.py` - Event-driven trigger for MinIO

### **Configuration**
- `docker-compose.yml` - Services orchestration
- `stack.yml` - OpenFaaS function definitions
- `monitoring/prometheus.yml` - Prometheus scrape config
- `monitoring/provisioning/` - Grafana dashboards

### **Scripts**
- `scripts/setup.sh` - Full environment setup
- `scripts/test.sh` - Test suite
- `scripts/setup-minio-webhook.sh` - Webhook configuration

### **This Demo**
- `demo_local.py` - Local demo server (NO DOCKER!)

---

## 🎓 Learning Points

### What You're Seeing:
1. **Serverless Functions** - How functions process images
2. **API Gateway Pattern** - Routing requests to processing functions
3. **Image Processing** - Real-time image manipulation
4. **Event-Driven Architecture** - MinIO webhooks triggering functions
5. **Monitoring** - Prometheus + Grafana for observability

### Key Concepts Demonstrated:
- ✅ **Scalability** - OpenFaaS auto-scales functions
- ✅ **Modularity** - Separate functions for different tasks
- ✅ **Asynchronous Processing** - Event-driven pipeline
- ✅ **Cloud Native** - Docker + Kubernetes ready
- ✅ **Observability** - Full metrics collection

---

## 🔗 Quick Links

| Link | Purpose |
|------|---------|
| http://localhost:5000 | API Home |
| http://localhost:5000/docs | **📖 Interactive API Docs** |
| http://localhost:5000/demo-image | Download test image |
| http://localhost:5000/health | Service health |
| http://localhost:5000/functions | List functions |

---

## 🛠️ What to Try Next

1. **Download demo image**: http://localhost:5000/demo-image
2. **Upload to Swagger UI** and try:
   - Resize to 200x200
   - Apply "sepia" filter
   - Enhance with brightness=1.2
   - Run full pipeline with multiple effects
3. **Combine filters**: Try edge → emboss → posterize
4. **Create variations**: Same image, different parameters

---

## 📚 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pillow (PIL) Image Library](https://python-pillow.org/)
- [OpenFaaS Documentation](https://docs.openfaas.com/)
- [MinIO Documentation](https://docs.min.io/)

---

## 🎉 Summary

✅ **This app demonstrates:**
- Real image processing pipeline
- RESTful API design
- Modern async Python development
- Cloud-native architecture principles
- Production-ready patterns

**All running locally without Docker!**

---

Generated: 2026-05-07 | Status: 🟢 RUNNING
