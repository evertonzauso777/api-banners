package controller

import (
	"api-banners/models"
	"api-banners/usecase"
	"api-banners/utils"
	"database/sql"
	"errors"
	"net/http"
	"strconv"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

type BannersController struct {
	usecase *usecase.UseCaseBanners
}

func NewControllerBanners(usecase *usecase.UseCaseBanners) *BannersController {
	return &BannersController{
		usecase: usecase,
	}
}

// CreateBanners godoc
// @Summary Cria Banner
// @Description Cria novo banner
// @Tags Banners
// @Accept multipart/form-data
// @Produce json
// @Param id_evento formData int true "ID do Evento"
// @Param titulo formData string true "Titulo do Banner"
// @Param ativo formData bool false "Status do banner"
// @Param imagem formData file false "Imagem do banner"
// @Success 201 {object} models.Banners
// @Failure 400 {object} models.ErrorResponse
// @Failure 500 {object} models.ErrorResponse
// @Router /banners [post]
func (con *BannersController) CreateBanners(c *gin.Context) {
	var banners models.Banners

	if strings.HasPrefix(c.ContentType(), "multipart/form-data") {
		idEvento, err := strconv.ParseInt(c.PostForm("id_evento"), 10, 64)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "id_evento inválido"})
			return
		}

		ativo := true
		ativoForm := c.PostForm("ativo")
		if ativoForm != "" {
			ativo, err = strconv.ParseBool(ativoForm)
			if err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": "ativo inválido"})
				return
			}
		}

		banners = models.Banners{
			ID_Evento:    idEvento,
			Titulo:       c.PostForm("titulo"),
			Data_Criacao: time.Now(),
			Ativo:        ativo,
		}

		if banners.Titulo == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "titulo é obrigatória"})
			return
		}

		file, err := c.FormFile("imagem")
		if err == nil {
			imagemURL, uploadErr := utils.UploadFileToB2(file, "banners")
			if uploadErr != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": uploadErr.Error()})
				return
			}

			banners.Imagem = imagemURL
		} else if !errors.Is(err, http.ErrMissingFile) {
			c.JSON(http.StatusBadRequest, gin.H{"error": "erro ao processar imagem"})
			return
		} else {
			if err := c.ShouldBindJSON(&banners); err != nil {
				c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
				return
			}
		}
	}

	err := con.usecase.InsertBanners([]models.Banners{banners})
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, banners)
}

// GetBanners godoc
// @Summary Lista banners
// @Description Retorna banners cadastrados
// @Tags Banners
// @Produce json
// @Success 200 {object} models.Banners
// @Failure 500 {object} models.ErrorResponse
// @Router /banners [get]
func (con *BannersController) GetBanners(c *gin.Context) {

	banners, err := con.usecase.GetBanners()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, banners)
}

// DeleteBanners godoc
// @Summary Remove banners
// @Description Remove banners pelo ID
// @Tags Banners
// @Produce json
// @Param id path string true "ID do Banner"
// @Success 200 {object} models.MessageResponse
// @Failure 404 {object} models.ErrorResponse
// @Failure 500 {object} models.ErrorResponse
// @Router /banners/{id} [delete]
func (con *BannersController) DeleteBanners(c *gin.Context) {
	id := c.Param("id")
	idBannner, err := strconv.ParseInt(id, 10, 64)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "ID inválido"})
		return
	}

	err = con.usecase.DeleteBanners(idBannner)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusNotFound, gin.H{"error": "Banner não encontrado"})
		return
	}
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Banner removido com sucesso"})
}
