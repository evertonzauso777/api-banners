package utils

import (
	"context"
	"log"
	"os"

	"github.com/joho/godotenv"
	"github.com/kurin/blazer/b2"
)

var B2Client *b2.Client

func init() {
	// Carregar variáveis do .env antes de ler as chaves do B2
	if err := godotenv.Load(); err != nil {
		log.Println("Arquivo .env não encontrado, usando variáveis de ambiente do sistema")
	}

	accountID := os.Getenv("B2_APPLICATION_KEY_ID") // Application Key ID
	appKey := os.Getenv("B2_APPLICATION_KEY")       // Application Key

	if accountID == "" || appKey == "" {
		log.Fatal("Erro: B2_APPLICATION_KEY_ID ou B2_APPLICATION_KEY não definidos")
	}

	var err error
	B2Client, err = b2.NewClient(context.Background(), accountID, appKey)
	if err != nil {
		log.Fatal("Erro ao conectar ao Backblaze B2:", err)
	}
}
