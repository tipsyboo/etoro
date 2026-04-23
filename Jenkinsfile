pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    triggers {
        githubPush()
    }

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
        stage('Initialize & Detect Changes') {
            steps {
                script {
                    // Check if this was a manual build
                    def causes = currentBuild.getBuildCauses().toString()
                    def isManual = causes.contains('UserCause') || causes.contains('UserIdCause')
                    
                    // Check for code/infra changes using git
                    def changedFiles = sh(script: 'git diff-tree --no-commit-id --name-only -r HEAD', returnStdout: true).trim()
                    def hasCodeChanges = changedFiles.split('\n').any { it.startsWith('simple-web/') || it == 'Jenkinsfile' }
                    
                    // Set a global flag for the rest of the pipeline
                    env.SHOULD_RUN_DEPLOYMENT = (isManual || hasCodeChanges).toString()
                    
                    echo "Manual Build: ${isManual}"
                    echo "Code Changes Detected: ${hasCodeChanges}"
                    echo "Deployment Logic Active: ${env.SHOULD_RUN_DEPLOYMENT}"
                }
            }
        }

        stage('Azure & AKS Authentication') {
            when {
                anyOf {
                    expression { params.ACTION == 'Destroy' }
                    expression { env.SHOULD_RUN_DEPLOYMENT == "true" }
                }
            }
            steps {
                script {
                    sh '''
                    az login -i
                    az aks get-credentials -n $CLUSTER_NAME -g $RESOURCE_GROUP -f $KUBECONFIG
                    kubelogin convert-kubeconfig -l msi --kubeconfig $KUBECONFIG
                    '''
                }
            }
        }

        stage('Lint Helm Chart') {
            when {
                allOf {
                    expression { params.ACTION == 'Deploy' }
                    expression { env.SHOULD_RUN_DEPLOYMENT == "true" }
                }
            }
            steps {
                sh 'helm lint ./simple-web'
            }
        }

        stage('Execute Action') {
            when {
                anyOf {
                    expression { params.ACTION == 'Destroy' }
                    expression { env.SHOULD_RUN_DEPLOYMENT == "true" }
                }
            }
            steps {
                script {
                    if (params.ACTION == 'Deploy') {
                        echo "Deploying ${RELEASE_NAME} to ${NAMESPACE}..."
                        sh "helm upgrade --install ${RELEASE_NAME} ./simple-web -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}"
                        sh "kubectl rollout status deployment/${RELEASE_NAME} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG} --timeout=90s"
                        
                        echo "Running internal smoke tests..."
                        sh "helm test ${RELEASE_NAME} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}"
                    } 
                    else if (params.ACTION == 'Destroy') {
                        echo "Destroying ${RELEASE_NAME} from ${NAMESPACE}..."
                        sh "helm uninstall ${RELEASE_NAME} -n ${NAMESPACE} --kubeconfig ${KUBECONFIG}"
                    }
                }
            }
        }

        stage('Verify External Access') {
            when {
                allOf {
                    expression { params.ACTION == 'Deploy' }
                    expression { env.SHOULD_RUN_DEPLOYMENT == "true" }
                }
            }
            steps {
                script {
                    def INGRESS_IP = sh(
                        script: "kubectl get svc nginx-ingress-controller -n ingress -o jsonpath='{.status.loadBalancer.ingress[0].ip}' --kubeconfig ${KUBECONFIG}",
                        returnStdout: true
                    ).trim()

                    echo "Testing external access to http://${INGRESS_IP}/pavelni ..."

                    timeout(time: 2, unit: 'MINUTES') {
                        waitUntil {
                            def status = sh(
                                script: "curl -s -o /dev/null -w '%{http_code}' http://${INGRESS_IP}/pavelni",
                                returnStdout: true
                            ).trim()
                            
                            if (status == "200") {
                                echo "Success: Received HTTP 200 OK from External IP"
                                return true
                            } else {
                                echo "Retrying... current status: ${status}"
                                sleep 5
                                return false
                            }
                        }
                    }
                }
            }
        }
    }

    post {
        always {
            sh "rm -f ${KUBECONFIG}"
            cleanWs()
        }
    }
}
