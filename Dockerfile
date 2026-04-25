FROM alpine:latest as builder

WORKDIR /app
COPY . .

# TODO: install dependencies and build the project

FROM alpine:latest
WORKDIR /app
COPY --from=builder /app .

entrypoint ["./eink-dash.py"]