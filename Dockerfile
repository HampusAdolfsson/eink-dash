# The dithers module uses Rust and needs to be compiled
FROM rust:1.91-alpine AS builder

WORKDIR /app

COPY dithers/ ./dithers/
RUN cargo build --release --manifest-path dithers/Cargo.toml

FROM ghcr.io/astral-sh/uv:alpine

WORKDIR /app

# Install Chromium for headless rendering
RUN apk add --no-cache chromium

# Install tzdata for timezone support
RUN apk add --no-cache tzdata

# Override DNS to use public resolver (Adguard has issues with IPv6 AAAA lookups)
RUN echo "nameserver 1.1.1.1" > /etc/resolv.conf

# Copy project files
COPY --from=builder /app/dithers/target/release/dithers /usr/local/bin/dithers
RUN chmod +x /usr/local/bin/dithers
COPY --exclude=dithers/ --exclude=driver/ . .

# Install Python dependencies for all workspace members
RUN uv sync --frozen --all-packages

# Print statements are (fully) buffered when running in docker, we want to disable
# that so we get live output from `docker run`.
ENV PYTHONUNBUFFERED=1

# Set your timezone here
ENV TZ="Europe/Berlin"

ENTRYPOINT ["uv", "run", "eink-dash.py"]