package main

import (
	"api-banners/controller"
	"api-banners/database"
	"api-banners/repository"
	"api-banners/usecase"
	"api-banners/utils"
	"log"

	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
	swaggerFiles "github.com/swaggo/files"
	ginSwagger "github.com/swaggo/gin-swagger"

	_ "api-banners/docs"
)

// @title API Banners
// @version 1.0
// @description API utilizada no site tickets.zauso-dev.com.br
// @host api-banners.zauso-dev.com.br
// @BasePath /
func main() {
	// Carregar variáveis do .env
	if err := godotenv.Load(); err != nil {
		log.Println("Arquivo .env não encontrado, usando variáveis de ambiente do sistema")
	}

	// Conectar ao banco de dados
	err := database.Connect()
	if err != nil {
		log.Fatal("Erro ao conectar ao banco", err)
	}
	defer database.DB.Close()

	router := gin.Default()

	utils.LoadCors(router)

	router.OPTIONS("/*path", func(c *gin.Context) {
		c.Status(200)
	})

	repository_banners := repository.NewRepositoryBanners(database.DB)
	usecase_banners := usecase.NewUseCaseBanners(repository_banners)
	ctrl := controller.NewControllerBanners(usecase_banners)

	router.GET("/banners", ctrl.GetBanners)
	router.POST("/banners", ctrl.CreateBanners)
	router.DELETE("/banners/:id", ctrl.DeleteBanners)

	// Swagger
	router.GET("/swagger/*any", ginSwagger.WrapHandler(swaggerFiles.Handler))
	log.Printf("Swagger disponível em http://localhost:%s/swagger/index.html", "8080")

	router.Run(":8080")

}
