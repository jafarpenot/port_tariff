# Port Tariff Calculator — runs the Streamlit UI (app.py) by default.
# See README "Option A — Docker" for how to run it, and how to run the
# test suite in this same image instead (`docker compose run app pytest`).

FROM python:3.12-slim

WORKDIR /app

# Plain pip only — no uv inside the image. Keeps the image minimal and
# matches "verify pip install -e . works" (README §Packaging).
# Upgrade pip first: an older pip's resolver (whatever a cached base
# image happens to ship) can fail to resolve this dependency set even
# though it's perfectly satisfiable — don't depend on base-image vintage.
RUN pip install --no-cache-dir --upgrade pip

COPY . .
# `[extraction]` is needed at runtime now too: app.py's "Extract New
# Tariff" page (pages/1_Extract_New_Tariff.py) runs the extraction
# pipeline, not just the calculator.
RUN pip install --no-cache-dir -e ".[extraction]"

EXPOSE 8501

# ANTHROPIC_API_KEY (calculator) and OPENAI_API_KEY (extraction) are both
# read from the environment at runtime (docker-compose.yml passes them
# through) — never baked into this image, never committed.
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
