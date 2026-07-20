# Dockerfile
# Use a imagem oficial do Go
FROM golang:1.25-alpine

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY go.mod go.sum ./

# Baixar dependências
RUN go mod download

# Copiar código fonte
COPY . .

# Build dos binarios
RUN go build -o main .

# Expor a porta que a aplicação usa
EXPOSE 8080

# Comando para executar a aplicação
CMD ["./main"]