pipeline {
    agent any

    parameters {
        choice(name: 'ACTION', choices: ['Deploy', 'Destroy'], description: 'Select the Helm action to perform')
    }

    environment {
        NAMESPACE = "pavelni"
        RELEASE_NAME = "simple-web"
        RESOURCE_GROUP = "devops-interview-rg"
        CLUSTER_NAME = "devops-interview-aks"
        KUBECONFIG = "${WORKSPACE}/.kube/config"
    }

    stages {
        stage('Azure & AKS Authentication') {
            steps {
                script {
                    sh '''
                    az login -i
                    
                    # Fetch cluster credentials into the workspace-specific kubeconfig
                    az aks get-credentials -n $CLUSTER_NAME -g $RESOURCE_GROUP -f $KUBECONFIG
                    
                    # Convert auth for MSI
                    kubelogin convert-kubeconfig -l msi --kubeconfig $KUBECONFIG
                    '''
                }
            }
        }

        stage('Lint Helm Chart') {
            when {
                expression { params.ACTION == 'Deploy' }
            }
            steps {
                sh 'helm lint ./simple-web'
            }
        }

        stage('Execute Action') {
            steps {
                script {
                    if (params.ACTION == 'Deploy') {
                        echo "Deploying ${RELEASE_NAME} to ${NAMESPACE}..."
                        sh "helm upgrade --install ${RELEASE_NAME} ./simple-web -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}"
                    } 
                    else if (params.ACTION == 'Destroy') {
                        echo "Destroying ${RELEASE_NAME} from ${NAMESPACE}..."
                        sh "helm uninstall ${RELEASE_NAME} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}"
                    }
                }
            }
        }
    }

    post {
        always {
            sh 'rm -f ${KUBECONFIG}'
            cleanWs()
        }
    }
}
