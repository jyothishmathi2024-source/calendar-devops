
pipeline {
    agent any

    environment {
        KUBECONFIG = '/tmp/jenkins-kubeconfig.yaml'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Source code checkout completed by Jenkins.'
                sh 'git status --short'
            }
        }

        stage('Check Tools') {
            steps {
                sh 'python3 --version'
                sh 'docker --version'
                sh 'kubectl version --client'
            }
        }

        stage('Test Application') {
            steps {
                sh '''
                    python3 -m pip install -r requirements.txt
                    python3 -m pytest -q
                '''
            }
        }

        stage('Verify Kubernetes') {
            steps {
                withCredentials([
                    string(
                        credentialsId: 'k8s-deployer-token',
                        variable: 'K8S_TOKEN'
                    )
                ]) {
                    sh '''
                        test -f "$KUBECONFIG"
                        kubectl --kubeconfig="$KUBECONFIG" \
                          get deployments
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Calendar CI pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check Console Output.'
        }
    }
}
