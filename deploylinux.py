#!/usr/bin/env python3
"""
Script para build, push e atualização de deployment - Versão Linux
"""

import subprocess
import re
import datetime
import os
import sys
from pathlib import Path

class DockerDeployer:
    def __init__(self, dockerhub_username, dockerhub_password, repository_name, path):
        self.dockerhub_username = dockerhub_username
        self.dockerhub_password = dockerhub_password
        self.repository_name = repository_name
        self.deployment_file = f"pipeline/{path}/deployment.yaml"

    def run_command(self, command, check=True):
        """Executa um comando shell no Linux."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                check=check,
                capture_output=True,
                text=True,
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Erro ao executar comando: {command}")
            print(f"Saída de erro: {e.stderr}")
            sys.exit(1)

    def check_prerequisites(self):
        """Verifica pré-requisitos básicos."""
        print("Verificando pré-requisitos...")

        if not Path("Dockerfile").exists():
            print("ERRO: Dockerfile não encontrado!")
            sys.exit(1)

        if not Path(self.deployment_file).exists():
            print(f"ERRO: Arquivo de deployment não encontrado: {self.deployment_file}")
            sys.exit(1)

        # Verifica se o Docker está instalado
        try:
            self.run_command("docker --version")
            print("✓ Docker encontrado")
        except Exception:
            print("ERRO: Docker não está instalado ou não está no PATH")
            sys.exit(1)

        # Verifica se buildx está disponível
        try:
            self.run_command("docker buildx version")
            print("✓ Docker Buildx disponível")
        except Exception:
            print("ERRO: Docker Buildx não está instalado ou configurado")
            sys.exit(1)

    def docker_login(self):
        """Faz login no Docker Hub usando --password-stdin (seguro)."""
        print("Fazendo login no DockerHub...")
        login_cmd = ["docker", "login", "-u", self.dockerhub_username, "--password-stdin"]
        try:
            process = subprocess.Popen(
                login_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(input=self.dockerhub_password)

            if process.returncode == 0:
                print("✓ Login no DockerHub realizado com sucesso!")
            else:
                print(f"ERRO: Falha no login no DockerHub: {stderr}")
                sys.exit(1)
        except Exception as e:
            print(f"ERRO no login: {e}")
            sys.exit(1)

    def generate_version(self):
        """Gera uma tag de versão baseada no timestamp atual."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        return f"v{timestamp}"

    def build_image(self, version):
        """Constrói a imagem Docker com suporte multiplataforma (linux/arm64)."""
        image_name = f"{self.dockerhub_username}/{self.repository_name}:{version}"
        image_latest = f"{self.dockerhub_username}/{self.repository_name}:latest"

        print(f"Construindo imagem Docker: {image_name}")
        build_cmd = [
            "docker", "buildx", "build",
            "--platform", "linux/arm64",
            "-t", image_name,
            "-t", image_latest,
            "--push",  # ← Empurra diretamente; opcional, mas evita push separado
            "."
        ]

        print("Executando build com push integrado...")
        process = subprocess.Popen(
            build_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Exibe saída em tempo real (essencial para Jenkins)
        for line in process.stdout:
            print(line, end="")

        process.wait()

        if process.returncode == 0:
            print("\n✓ Build e push da imagem concluídos com sucesso!")
            return image_name
        else:
            print("\nERRO: Falha no build da imagem Docker")
            sys.exit(1)

    def push_image(self, image_name):
        """
        [Opcional] Se você NÃO usar --push no build, use este método.
        Mas recomendamos usar --push diretamente no buildx para evitar duplicação.
        """
        # Esta função pode ser removida se usar --push acima.
        # Mantida aqui por compatibilidade, mas desativada por padrão.
        pass

    def update_deployment(self, image_name):
        """Atualiza o deployment.yaml com a nova tag de imagem."""
        print(f"Atualizando arquivo de deployment: {self.deployment_file}")

        # Backup
        backup_file = f"{self.deployment_file}.backup"
        content = Path(self.deployment_file).read_text()
        Path(backup_file).write_text(content)
        print(f"Backup criado: {backup_file}")

        # Substitui a linha da imagem
        pattern = rf"image:\s*{re.escape(self.dockerhub_username)}/{re.escape(self.repository_name)}:.+"
        replacement = f"image: {image_name}"
        new_content = re.sub(pattern, replacement, content, count=1)

        # Salva
        Path(self.deployment_file).write_text(new_content)
        print("✓ Arquivo deployment.yaml atualizado com sucesso!")

        # Validação
        if image_name in new_content:
            print("✓ Verificação: Imagem atualizada corretamente no YAML")
        else:
            print("ERRO: A imagem não foi encontrada após atualização")
            sys.exit(1)

    def run(self):
        """Executa o fluxo completo de deploy."""
        print("=" * 60)
        print("🚀 Iniciando processo de build, push e atualização do deployment...")
        print("=" * 60)

        self.check_prerequisites()
        self.docker_login()

        version = self.generate_version()
        print(f"🔖 Versão gerada: {version}")

        image_name = self.build_image(version)
        # Nota: push já feito via --push no buildx
        self.update_deployment(image_name)

        print("=" * 60)
        print("✅ Processo concluído com sucesso!")
        print(f"📦 Imagem: {image_name}")
        print(f"📝 Arquivo atualizado: {self.deployment_file}")
        print("=" * 60)


if __name__ == "__main__":
    DOCKERHUB_USERNAME = os.getenv("DOCKERHUB_USERNAME")
    DOCKERHUB_PASSWORD = os.getenv("DOCKERHUB_PASSWORD")
    REPOSITORY_NAME = os.getenv("REPOSITORY_NAME", "api-savings-arm64")
    PATH_DEPLOYMENT = os.getenv("PATH_DEPLOYMENT", "k8s/api")

    if not DOCKERHUB_USERNAME or not DOCKERHUB_PASSWORD:
        print("ERRO: Variáveis DOCKERHUB_USERNAME e DOCKERHUB_PASSWORD são obrigatórias.")
        print("Defina-as no arquivo pipeline/.env ou como variáveis de ambiente.")
        sys.exit(1)

    deployer = DockerDeployer(DOCKERHUB_USERNAME, DOCKERHUB_PASSWORD, REPOSITORY_NAME, PATH_DEPLOYMENT)
    deployer.run()