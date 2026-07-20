package usecase

import (
	"api-banners/models"
	"api-banners/repository"
)

type UseCaseBanners struct {
	repo *repository.RepositoryBanners
}

func NewUseCaseBanners(repository *repository.RepositoryBanners) *UseCaseBanners {
	return &UseCaseBanners{
		repo: repository,
	}
}

func (r *UseCaseBanners) InsertBanners(banners []models.Banners) error {
	err := r.repo.InsertBanners(banners)
	if err != nil {
		return err
	}

	return nil
}

func (r *UseCaseBanners) GetBanners() ([]models.Banners, error) {

	banners, err := r.repo.GetBanners()
	if err != nil {
		return nil, err
	}

	return banners, nil
}

func (r *UseCaseBanners) DeleteBanners(id int64) error {
	err := r.repo.DeleteBanners(id)
	if err != nil {
		return err
	}

	return nil
}
