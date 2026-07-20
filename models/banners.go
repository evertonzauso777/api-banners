package models

import (
	"time"
)

type Banners struct {
	ID           int64     `json:"id_banner"`
	ID_Evento    int64     `json:"id_evento"`
	Titulo       string    `json:"titulo"`
	Imagem       string    `json:"imagem"`
	Ativo        bool      `json:"ativo"`
	Data_Criacao time.Time `json:"data_criacao"`
}
