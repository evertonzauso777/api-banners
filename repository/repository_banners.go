package repository

import (
	"api-banners/models"
	"database/sql"
	"log"
)

type RepositoryBanners struct {
	db *sql.DB
}

func NewRepositoryBanners(db *sql.DB) *RepositoryBanners {
	return &RepositoryBanners{
		db: db,
	}
}

func (r *RepositoryBanners) InsertBanners(banners []models.Banners) error {
	for _, b := range banners {

		query := `
			INSERT INTO public.banners(
				id_evento, titulo, imagem, ativo, data_criacao)
				VALUES ($1, $2, $3, $4, $5);
		`

		_, err := r.db.Exec(query,
			b.ID_Evento,
			b.Titulo,
			b.Imagem,
			b.Ativo,
			b.Data_Criacao,
		)

		if err != nil {
			log.Printf("Erro ao inserir banner: %v", err)
			return err
		}
	}

	return nil
}

func (r *RepositoryBanners) GetBanners() ([]models.Banners, error) {

	query := `SELECT id_banner, id_evento, titulo, imagem, ativo, data_criacao FROM public.banners where ativo = true`
	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var banners []models.Banners
	for rows.Next() {
		var b models.Banners
		err := rows.Scan(&b.ID, &b.ID_Evento, &b.Titulo, &b.Imagem, &b.Ativo, &b.Data_Criacao)
		if err != nil {
			return nil, err
		}
		banners = append(banners, b)
	}

	return banners, nil
}

func (r *RepositoryBanners) DeleteBanners(id int64) error {
	query := `DELETE FROM public.banners WHERE id_banner = $1`
	result, err := r.db.Exec(query, id)
	if err != nil {
		return err
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return err
	}
	if rowsAffected == 0 {
		return sql.ErrNoRows
	}

	return nil
}
