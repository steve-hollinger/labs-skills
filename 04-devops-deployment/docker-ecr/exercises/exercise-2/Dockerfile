# EXERCISE 2: Convert this to a multi-stage build
# Goal: Reduce image size from ~800MB to <15MB

FROM golang:1.22

WORKDIR /app

COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN go build -o server ./cmd/server

EXPOSE 8080
CMD ["./server"]
