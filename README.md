# Projeto API Banners

## Descrição do Projeto

Este projeto é uma API RESTful que gerencia banners para eventos. Ela permite criar, ler, atualizar e deletar banners através de endpoints definidos. A API integra-se com um banco de dados PostgreSQL e possui endpoints Swagger para documentação interativa.

## Arquitetura

A arquitetura do projeto é composta por camadas separadas:

1. **Controller**: Define as interfaces HTTP e processa as requisições.
2. **Usecase**: Contém a lógica de negócios da aplicação.
3. **Repository**: Abstrai as operações de banco de dados.
4. **Models**: Definição das estruturas de dados utilizadas na aplicação.
5. **Utils**: Funções utilitárias como CORS e uploads de arquivos.

## Como Rodar

### Pré-requisitos
- Go >= 1.16
- PostgreSQL >= 12
- .env file com as variáveis de ambiente definidas (veja `.env.example`)

### Instalação e Execução

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-repositorio/api-banners.git
   cd api-banners
   ```

2. Crie um arquivo `.env` com as variáveis de ambiente necessárias (veja `.env.example`).

3. Execute a aplicação:
   ```bash
   go run main.go
   ```

4. Acesse os endpoints da API no Swagger:
   ```
   http://localhost:8080/swagger/
   ```

## Dependências

As dependências do projeto estão definidas em `go.mod`. Para instalar as dependências, execute:

```bash
go mod tidy
```

## Endpoints

### GET /banners
- **Descrição**: Retorna uma lista de banners.
- **Parâmetros**:
  - `page` (opcional): Número da página. Padrão é 1.
  - `per_page` (opcional): Quantidade de itens por página. Padrão é 20.
- **Resposta**:
  ```json
  {
    "current_page": 1,
    "per_page": 20,
    "total": 50,
    "total_pages": 3,
    "data": [
      {
        "id_banner": 1,
        "id_evento": 101,
        "titulo": "Banner Evento",
        "imagem": "http://example.com/banner.png",
        "ativo": true,
        "data_criacao": "2023-04-01T10:00:00Z"
      },
      ...
    ]
  }
  ```

### POST /banners
- **Descrição**: Cria um novo banner.
- **Requisição**:
  ```json
  {
    "id_evento": 101,
    "titulo": "Novo Banner",
    "imagem": "http://example.com/new-banner.png",
    "ativo": true
  }
  ```
- **Resposta**:
  ```json
  {
    "message": "Banner criado com sucesso!"
  }
  ```

### DELETE /banners/:id
- **Descrição**: Exclui um banner por ID.
- **Parâmetros**:
  - `id`: Identificador do banner a ser excluído.

## Swagger

A documentação da API está disponível no Swagger:

```
http://localhost:8080/swagger/
```

Isso inclui todas as operações disponíveis, seus parâmetros e respostas esperadas.