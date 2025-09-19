pipeline {
    agent any
    environment {
        DOCKER_HUB_REPO ="manjudata/predicthub"
        DOCKER_HUB_CREDENTIALS_ID="gitops-dockerhub-token"
    }
    stages {
        stage('Checkout Github') {
            steps {
                echo 'Checking out code from GitHub...'
		checkout scmGit(branches: [[name: '*/main']], extensions: [], userRemoteConfigs: [[credentialsId: 'github-new-token', url: 'https://github.com/manjudata/PREDICT-MLOPS.git']])
		    }
        }        
        stage('Build Docker Image') {
            steps {
                script{
                    echo 'Building Docker image...'
                    dockerImage = docker.build("${DOCKER_HUB_REPO}:latest")
                }
            }
        }
        stage('Push Image to DockerHub') {
            steps {
                script{
                    echo 'Pushing Docker image to DockerHub...'
                    docker.withRegistry('https://registry.hub.docker.com' , "${DOCKER_HUB_CREDENTIALS_ID}") {
                       dockerImage.push('latest')
                    }
                }
            }
        }
        stage('Install Kubectl & ArgoCD CLI') {
            steps {
               sh'''
               echo 'installing Kubectl & ArgoCD cli...'
               curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
               chmod +x kubectl
               mv kubectl /usr/local/bin/kubectl
               curl -sSL -o /usr/local/bin/argocd https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
               chmod +x /usr/local/bin/argocd
               '''
            }
        }
        stage('Check Argo token credential') {
            steps {
            withCredentials([string(credentialsId: 'argocd-token', variable: 'ARGO_TOKEN')]) {
            sh 'echo "ARGO token available"'
             }
           }
        }

        stage('Apply Kubernetes & Sync App with ArgoCD') {
            steps {
                withCredentials([string(credentialsId: 'argocd-token', variable: 'ARGO_TOKEN')]) {
                sh '''#!/usr/bin/env bash
                set -eu
                 export ARGOCD_SERVER="34.121.241.126:30135"
                 export ARGOCD_AUTH_TOKEN="$ARGO_TOKEN"
                 ARGS="--insecure --grpc-web"
                 
                 # No interactive login; the token is used on each command
                 argocd $ARGS app sync gitopsapp
                 argocd $ARGS app wait gitopsapp --health --sync
                 '''
                }
            }
        }
    }
}