// utils/b2upload.go
package utils

import (
	"context"
	"fmt"
	"io"
	"mime/multipart"
	"os"
	"path/filepath"

	"github.com/google/uuid"
)

func UploadFileToB2(file *multipart.FileHeader, folder string) (string, error) {
	src, err := file.Open()
	if err != nil {
		return "", fmt.Errorf("falha ao abrir arquivo: %w", err)
	}
	defer src.Close()

	// Nome único
	ext := filepath.Ext(file.Filename)
	safeName := uuid.New().String() + ext
	filename := fmt.Sprintf("%s/%s", folder, safeName)

	bucketName := os.Getenv("B2_BUCKET_NAME")
	if bucketName == "" {
		return "", fmt.Errorf("B2_BUCKET_NAME não definido")
	}

	bucket, err := B2Client.Bucket(context.Background(), bucketName)
	if err != nil {
		return "", fmt.Errorf("falha ao obter bucket: %w", err)
	}
	obj := bucket.Object(filename)

	// NewWriter() também não exige context
	w := obj.NewWriter(context.Background())
	defer w.Close()

	if _, err = io.Copy(w, src); err != nil {
		return "", fmt.Errorf("falha ao enviar dados: %w", err)
	}

	publicURL := fmt.Sprintf("https://f005.backblazeb2.com/file/%s/%s", bucketName, filename)
	return publicURL, nil
}
