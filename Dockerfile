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
RUN pip install --no-cache-dir -e .

EXPOSE 8501

# ANTHROPIC_API_KEY is read from the environment at runtime (docker-compose.yml
# passes it through) — never baked into this image, never committed.
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
