from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from datetime import datetime
import os, json, re

BASE = Path(__file__).resolve().parent.parent
STATIC = BASE / "static"
EXPORTS = STATIC / "exports"
PANELS = STATIC / "panels"
EXPORTS.mkdir(parents=True, exist_ok=True)
PANELS.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="ComicCraft — AI Comic Story Creator", version="1.0.0")
app.mount("/static", StaticFiles(directory=STATIC), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))

DEMO_MODE = os.getenv("DEMO_MODE", "true").lower() == "true"

def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", value).strip("_")[:50] or "comic"

def demo_panels(prompt, character, setting, tone, art_style):
    return [
        {
            "number": 1, "title": "The Spark",
            "scene": f"{character} discovers that something unusual is happening in {setting}.",
            "caption": "A strange feeling fills the air...",
            "narration": f"{character} takes the first brave step into the story. The mood is {tone}.",
            "dialogue": f'"Okay... this is definitely not normal," {character} whispers.',
            "image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=1200&q=85",
            "image_prompt": f"{art_style} comic panel, {character}, {setting}, mysterious beginning, cinematic lighting"
        },
        {
            "number": 2, "title": "Into the Unknown",
            "scene": f"The path leads {character} deeper into {setting}, where the first real clue appears.",
            "caption": "CRACK! A branch snaps nearby.",
            "narration": "The silence breaks. Every shadow seems to move for a second.",
            "dialogue": '"Who is there?"',
            "image": "https://images.unsplash.com/photo-1511497584788-876760111969?auto=format&fit=crop&w=1200&q=85",
            "image_prompt": f"{art_style} comic panel, {character} exploring {setting}, suspense, dynamic perspective"
        },
        {
            "number": 3, "title": "The Turning Point",
            "scene": "A hidden secret changes what the hero thought they knew.",
            "caption": "WHOOSH! The world seems to freeze.",
            "narration": f"{character} realizes the adventure is much bigger than the original idea: {prompt}.",
            "dialogue": '"Then I have to finish what I started."',
            "image": "https://images.unsplash.com/photo-1534796636912-3b95b3ab5986?auto=format&fit=crop&w=1200&q=85",
            "image_prompt": f"{art_style} comic panel, dramatic revelation, {character}, glowing discovery, epic atmosphere"
        },
        {
            "number": 4, "title": "The Challenge",
            "scene": "The final obstacle rises between the hero and the answer.",
            "caption": "BOOM! The challenge begins.",
            "narration": f"With courage and creativity, {character} faces the impossible.",
            "dialogue": '"I came this far. I am not turning back now!"',
            "image": "https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?auto=format&fit=crop&w=1200&q=85",
            "image_prompt": f"{art_style} comic panel, heroic confrontation, {character}, {setting}, energetic action"
        },
        {
            "number": 5, "title": "A New Page",
            "scene": "The adventure reaches a satisfying ending, while leaving room for another chapter.",
            "caption": "The wind settles. A new day begins.",
            "narration": f"{character} smiles, knowing that every great story starts with one small idea.",
            "dialogue": '"This is only the beginning."',
            "image": "https://images.unsplash.com/photo-1500534623283-312aade485b7?auto=format&fit=crop&w=1200&q=85",
            "image_prompt": f"{art_style} comic panel, hopeful ending, {character}, sunrise, cinematic comic art"
        }
    ]

def generate_with_gemini(prompt, character, setting, tone, art_style):
    # Optional integration. DEMO_MODE=true keeps the site runnable without API keys.
    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        instruction = f"""
Create a 5-panel comic outline as JSON only.
Story idea: {prompt}
Main character: {character}
Setting: {setting}
Tone: {tone}
Art style: {art_style}
Return an array of 5 objects with keys:
number, title, scene, caption, narration, dialogue, image_prompt.
"""
        response = client.models.generate_content(
            model=os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash"),
            contents=instruction
        )
        text = response.text.strip().replace("```json", "").replace("```", "")
        panels = json.loads(text)
        for i, panel in enumerate(panels, 1):
            panel["number"] = i
            panel.setdefault("image", "")
        return panels
    except Exception:
        return demo_panels(prompt, character, setting, tone, art_style)

def make_pdf(panels, title, filename):
    from fpdf import FPDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    for panel in panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 22)
        pdf.multi_cell(0, 12, title)
        pdf.set_font("Helvetica", "B", 16)
        pdf.multi_cell(0, 10, f"Panel {panel['number']}: {panel['title']}")
        pdf.set_font("Helvetica", "", 12)
        for key in ("scene", "caption", "narration", "dialogue"):
            value = panel.get(key, "")
            if value:
                pdf.ln(3)
                pdf.set_font("Helvetica", "B", 11)
                pdf.cell(0, 7, key.title())
                pdf.ln()
                pdf.set_font("Helvetica", "", 11)
                pdf.multi_cell(0, 7, str(value))
    path = EXPORTS / filename
    pdf.output(str(path))
    return path

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/generate", response_class=HTMLResponse)
async def generate(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    if not story_prompt.strip() or not character_name.strip():
        raise HTTPException(400, "Story prompt and character name are required.")
    panels = demo_panels(story_prompt, character_name, setting, tone, art_style) if DEMO_MODE else generate_with_gemini(
        story_prompt, character_name, setting, tone, art_style
    )
    comic_title = f"{character_name}: {story_prompt[:45].strip()}"
    return templates.TemplateResponse("preview.html", {
        "request": request, "panels": panels, "title": comic_title,
        "character": character_name, "setting": setting, "tone": tone, "art_style": art_style
    })

@app.post("/generate-comic/json")
async def generate_json(payload: dict):
    required = ["story_prompt", "character_name", "setting", "tone", "art_style"]
    if any(not str(payload.get(k, "")).strip() for k in required):
        raise HTTPException(400, "Missing required fields.")
    panels = demo_panels(payload["story_prompt"], payload["character_name"], payload["setting"], payload["tone"], payload["art_style"])
    title = f"{payload['character_name']}: {payload['story_prompt'][:45]}"
    return {"title": title, "layout": panels, "mode": "demo" if DEMO_MODE else "gemini"}

@app.post("/export")
async def export_pdf(request: Request):
    data = await request.json()
    panels = data.get("panels", [])
    title = data.get("title", "ComicCraft Comic")
    if not panels:
        raise HTTPException(400, "No comic panels supplied.")
    filename = f"{safe_name(title)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    path = make_pdf(panels, title, filename)
    return {"download_url": f"/download/{path.name}"}

@app.get("/download/{filename}")
async def download(filename: str):
    path = EXPORTS / safe_name(filename) + ".pdf" if not filename.endswith(".pdf") else EXPORTS / safe_name(filename)
    # safe_name can preserve the .pdf poorly, so resolve by exact filename after sanitizing.
    candidate = EXPORTS / re.sub(r"[^a-zA-Z0-9_.-]", "_", filename)
    if not candidate.exists():
        raise HTTPException(404, "File not found.")
    return FileResponse(candidate, media_type="application/pdf", filename=candidate.name)

@app.get("/test-image")
async def test_image():
    return JSONResponse({"status": "ok", "message": "Image generation test route is available. Demo mode uses remote preview images."})

@app.get("/health")
async def health():
    return {"status": "healthy", "demo_mode": DEMO_MODE}
