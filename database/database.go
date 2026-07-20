package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"
	"strconv"

	"github.com/joho/godotenv"
	_ "github.com/lib/pq"
)

var DB *sql.DB

func Connect() error {
	// Carregar variaveis de ambiente env
	err := godotenv.Load()
	if err != nil {
		log.Println("Arquivo .env não encontrado, usando variáveis de ambiente do sistema")
	}

	host := getEnvOrDefault("DB_HOST", "localhost")
	port := getEnvOrDefault("DB_PORT", "5432")
	user := getEnvOrDefault("DB_USER", "postgres")
	password := getEnvOrDefault("DB_PASSWORD", "")
	dbname := getEnvOrDefault("DB_NAME", "zausoeventosdb")
	sslmode := getEnvOrDefault("DB_SSLMODE", "disable")

	// Validar porta
	portInt, err := strconv.Atoi(port)
	if err != nil || portInt <= 0 {
		port = "5432"
	}

	// Formatar string de conexão corretamente
	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=%s",
		host, port, user, password, dbname, sslmode)

	log.Printf("Conectando ao PostgreSQL: host=%s, port=%s, dbname=%s", host, port, dbname)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		return fmt.Errorf("erro ao conectar ao banco: %v", err)
	}

	err = db.Ping()
	if err != nil {
		return fmt.Errorf("erro ao testar conexão: %v", err)
	}

	DB = db
	log.Println("Conectado ao PostgreSQL com sucesso!")

	return nil
}

func getEnvOrDefault(key, defaultValue string) string {
	value := os.Getenv(key)
	if value == "" {
		return defaultValue
	}
	return value
}
