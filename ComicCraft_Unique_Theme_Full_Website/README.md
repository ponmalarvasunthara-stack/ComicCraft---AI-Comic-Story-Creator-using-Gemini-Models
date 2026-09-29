# ComicCraft — Unique Frontend Edition

A FastAPI + Jinja2 AI comic creator inspired by the supplied ComicCraft project specification.

## What is included

- Distinct editorial/comic-book frontend theme (black, cream, hot-orange, lime)
- Responsive creator console
- 5-panel comic preview
- Story prompt, character, setting, tone and art-style inputs
- JSON API endpoint
- PDF export
- Demo mode so the project can run immediately without an API key
- Optional Gemini integration hook
- Health/test endpoints

The original specification describes Gemini Flash for structured 5-panel outlines, Gemini Pro for detailed narration/dialogue, Stable Diffusion for comic illustrations, FastAPI/Jinja2 for the application layer, and FPDF for PDF export. This edition keeps that overall workflow while making the frontend visually distinct. 

## Run on Windows

1. Install Python 3.10+.
2. Open a terminal in this folder.
3. Create an environment:

   python -m venv env
   env\Scripts\activate

4. Install:

   pip install -r requirements.txt

5. Copy `.env.example` to `.env`.
6. For the first test, keep:

   DEMO_MODE=true

7. Start:

   uvicorn app.main:app --reload

8. Open:

   http://127.0.0.1:8000

API docs:

   http://127.0.0.1:8000/docs

## AI mode

Set `DEMO_MODE=false` and provide `GEMINI_API_KEY`.

The code uses the current `google-genai` client and defaults to `gemini-2.5-flash`. The supplied project document names Gemini 1.5 Flash/Pro and Stable Diffusion; model availability can change, so the model name is configurable through `GEMINI_TEXT_MODEL`.

Image generation in this starter uses preview image URLs in demo mode. A production version can connect the `image_generator.py` stage to Hugging Face Diffusers/Stable Diffusion and store generated files under `static/panels`.

## Project structure

ComicCraft_Unique_Theme/
  app/
    main.py
  templates/
    index.html
    preview.html
    export_success.html
  static/
    css/
      style.css
    panels/
    exports/
  .env.example
  requirements.txt
  README.md

## Main flow

Home -> POST /generate -> 5-panel preview -> POST /export -> PDF download.

The supplied specification also describes `/generate-comic/json` and `/test-image`; both are included here.
