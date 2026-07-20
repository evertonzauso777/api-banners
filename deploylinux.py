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
        self.deployment_paths = [
            Path("pipeline") / item.strip()
            for item in path.split(",")
            if item.strip()
        ]

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

        if not self.deployment_paths:
            print("ERRO: PATH_DEPLOYMENT está vazio.")
            sys.exit(1)

        missing_paths = [str(path) for path in self.deployment_paths if not path.exists()]
        if missing_paths:
            print(f"ERRO: Caminhos de deployment não encontrados: {', '.join(missing_paths)}")
            sys.exit(1)

        deployment_files = self.find_deployment_files()
        if not deployment_files:
            checked_paths = ", ".join(str(path) for path in self.deployment_paths)
            print(f"ERRO: Nenhum deployment.yaml encontrado em: {checked_paths}")
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

    def find_deployment_files(self):
        """Busca arquivos deployment.yaml nos caminhos configurados."""
        deployment_files = []

        for base_path in self.deployment_paths:
            if base_path.is_file() and base_path.name == "deployment.yaml":
                deployment_files.append(base_path)
                continue

            deployment_files.extend(sorted(base_path.rglob("deployment.yaml")))

        unique_files = sorted(set(deployment_files))
        return unique_files

    def update_deployments(self, image_name):
        """Atualiza todos os deployment.yaml com a nova tag de imagem."""
        deployment_files = self.find_deployment_files()
        pattern = rf"image:\s*{re.escape(self.dockerhub_username)}/{re.escape(self.repository_name)}:[^\s]+"
        replacement = f"image: {image_name}"

        updated_files = 0

        for deployment_file in deployment_files:
            print(f"Atualizando arquivo de deployment: {deployment_file}")

            content = deployment_file.read_text()
            backup_file = Path(f"{deployment_file}.backup")
            backup_file.write_text(content)
            print(f"Backup criado: {backup_file}")

            new_content, replacements = re.subn(pattern, replacement, content)
            deployment_file.write_text(new_content)

            if replacements > 0:
                print(f"✓ Imagem atualizada em {deployment_file} ({replacements} ocorrência(s))")
                updated_files += 1
            else:
                print(f"⚠️ Nenhuma imagem correspondente encontrada em {deployment_file}")

        if updated_files == 0:
            print("ERRO: A imagem não foi encontrada em nenhum deployment.yaml")
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
        self.update_deployments(image_name)

        print("=" * 60)
        print("✅ Processo concluído com sucesso!")
        print(f"📦 Imagem: {image_name}")
        print(f"📝 Caminhos atualizados: {', '.join(str(path) for path in self.deployment_paths)}")
        print("=" * 60)


if __name__ == "__main__":
    DOCKERHUB_USERNAME = os.getenv("DOCKERHUB_USERNAME")
    DOCKERHUB_PASSWORD = os.getenv("DOCKERHUB_PASSWORD")
    REPOSITORY_NAME = os.getenv("REPOSITORY_NAME", "api-savings-arm64")
    PATH_DEPLOYMENT = os.getenv("PATH_DEPLOYMENT", "k8s,worker")

    if not DOCKERHUB_USERNAME or not DOCKERHUB_PASSWORD:
        print("ERRO: Variáveis DOCKERHUB_USERNAME e DOCKERHUB_PASSWORD são obrigatórias.")
        print("Defina-as no arquivo pipeline/.env ou como variáveis de ambiente.")
        sys.exit(1)

    deployer = DockerDeployer(DOCKERHUB_USERNAME, DOCKERHUB_PASSWORD, REPOSITORY_NAME, PATH_DEPLOYMENT)
    deployer.run()