pipeline {
    agent any

    environment {
        // Docker Hub
        DOCKERHUB_USERNAME = credentials('dockerhub-username')
        DOCKERHUB_PASSWORD = credentials('dockerhub-password')

        // Projeto
        REPOSITORY_NAME = 'api-banners-arm64'
        PATH_DEPLOYMENT = 'k8s'

        // GitHub
        GH_OWNER = 'evertonzauso777'
        GH_REPO  = 'api-banners'
        TARGET_BRANCH = 'main'
        CI_BRANCH = "ci/update-manifest-${BUILD_NUMBER}"
    }

    stages {

        stage('Setup QEMU for multi-arch') {
            steps {
                sh '''
                    docker run --privileged --rm tonistiigi/binfmt --install all
                '''
            }
        }

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

              stage('Skip if merge from main to dev') {
            steps {
                withCredentials([
                    string(credentialsId: 'github-pat', variable: 'GH_TOKEN')
                ]) {
                    script {

                        def currentBranch = (env.GIT_BRANCH ?: '').replace('origin/', '')

                        if (currentBranch != 'dev') {
                            echo "Não é a branch 'dev' — ignorando verificação de merge."
                            return
                        }

                        // Fetch explícito do main
                        sh """
                            git fetch https://x-access-token:${GH_TOKEN}@github.com/${GH_OWNER}/${GH_REPO}.git main:refs/remotes/origin/main
                        """

                        def parentCount = sh(
                            script: 'git log -1 --pretty=%P | wc -w',
                            returnStdout: true
                        ).trim().toInteger()

                        if (parentCount <= 1) {
                            echo "Último commit não é merge — continuando."
                            return
                        }

                        def secondParent = sh(
                            script: 'git log -1 --pretty=%P | cut -d" " -f2',
                            returnStdout: true
                        ).trim()

                        def mainHead = sh(
                            script: 'git rev-parse refs/remotes/origin/main',
                            returnStdout: true
                        ).trim()

                        if (secondParent == mainHead) {
                            echo "⚠️ Merge detectado de 'main' para 'dev'. Abortando pipeline para evitar loop."
                            currentBuild.result = 'ABORTED'
                            error('Skipping CI due to main → dev merge')
                        }

                        echo "Merge detectado, mas não veio de 'main' — continuando..."
                    }
                }
            }
        }

        stage('Deploy to Registry & Update Manifest') {
            steps {
                sh '''
                    echo "Iniciando deploy com:"
                    echo "REPO: $REPOSITORY_NAME"
                    echo "PATH: $PATH_DEPLOYMENT"
                    python3 deploylinux.py
                '''
            }
        }

        stage('Commit & Push CI Branch') {
            steps {
                withCredentials([
                    string(credentialsId: 'github-pat', variable: 'GH_TOKEN')
                ]) {
                    sh '''#!/bin/bash
                        set -e

                        git config user.email "jenkins@ci.local"
                        git config user.name "Jenkins CI"

                        git checkout -b "$CI_BRANCH"

                        git add pipeline/

                        if git diff --staged --quiet; then
                            echo "Nenhuma mudança — PR não será criado."
                            exit 0
                        fi

                        git commit -m "Atualiza imagem automaticamente"

                        git remote set-url origin https://x-access-token:$GH_TOKEN@github.com/$GH_OWNER/$GH_REPO.git

                        git push origin "$CI_BRANCH"
                    '''
                }
            }
        }

        stage('Create Pull Request') {
            steps {
                withCredentials([
                    string(credentialsId: 'github-pat', variable: 'GH_TOKEN')
                ]) {
                    sh '''#!/bin/bash
                        set -e

                        curl -s -X POST \
                          -H "Authorization: Bearer $GH_TOKEN" \
                          -H "Accept: application/vnd.github+json" \
                          https://api.github.com/repos/$GH_OWNER/$GH_REPO/pulls \
                          -d "{
                                \\"title\\": \\"Atualiza manifesto automaticamente\\",
                                \\"head\\": \\"$CI_BRANCH\\",
                                \\"base\\": \\"$TARGET_BRANCH\\",
                                \\"body\\": \\"PR criada automaticamente pelo Jenkins\\"
                              }"
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker logout || true'
        }
    }
}
