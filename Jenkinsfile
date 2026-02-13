pipeline {
 agent any

 environment {
   DOCKER_IMAGE = "aslam2022bcs0092/wine-inference"
 }

 stages {

 stage('Checkout') {
   steps { checkout scm }
 }

 stage('Setup Python') {
   steps {
     sh '''
     python3 -m venv venv
     . venv/bin/activate
     pip install --upgrade pip
     pip install -r requirements.txt
     '''
   }
 }

 stage('Train') {
   steps {
     sh '''
     . venv/bin/activate
     python scripts/train.py
     '''
   }
 }

 stage('Read Metrics') {
   steps {
     script {
       def m = readJSON file: 'metrics.json'
       env.R2 = m.r2.toString()
       env.MSE = m.mse.toString()
       echo "R2=${env.R2}"
       echo "MSE=${env.MSE}"
     }
   }
 }

 stage('Compare') {
   steps {
     script {
       withCredentials([
         string(credentialsId: 'BEST_R2', variable: 'BEST_R2'),
         string(credentialsId: 'BEST_MSE', variable: 'BEST_MSE')
       ]) {

         if (env.R2.toFloat() > BEST_R2.toFloat() &&
             env.MSE.toFloat() < BEST_MSE.toFloat()) {
           env.DEPLOY = "true"
         } else {
           env.DEPLOY = "false"
         }
       }
     }
   }
 }

 stage('Docker Build') {
   when { expression { env.DEPLOY == "true" } }
   steps {
     sh 'docker build -t $DOCKER_IMAGE:${BUILD_NUMBER} .'
   }
 }

 stage('Docker Push') {
   when { expression { env.DEPLOY == "true" } }
   steps {
     withCredentials([usernamePassword(
       credentialsId: 'docker-hub-credentials',
       usernameVariable: 'USER',
       passwordVariable: 'PASS'
     )]) {
       sh '''
       echo "$PASS" | docker login -u "$USER" --password-stdin
       docker push $DOCKER_IMAGE:${BUILD_NUMBER}
       docker tag $DOCKER_IMAGE:${BUILD_NUMBER} $DOCKER_IMAGE:latest
       docker push $DOCKER_IMAGE:latest
       '''
     }
   }
 }

 }

 post {
   always {
     archiveArtifacts artifacts: '*.json'
   }
 }
}
