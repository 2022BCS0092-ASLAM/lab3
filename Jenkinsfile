pipeline {
  agent any

  environment {
    IMAGE = "aslam2022bcs0092/wine-inference"
    CONTAINER_NAME = "wine-api-test"
    PORT = "8000"
  }

  stages {

    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Pull Image') {
      steps {
        sh "docker pull $IMAGE"
      }
    }

    stage('Run Container') {
      steps {
        sh """
          docker stop $CONTAINER_NAME || true
          docker rm $CONTAINER_NAME || true
          docker run -d -p $PORT:8000 --name $CONTAINER_NAME $IMAGE
        """
      }
    }

    stage('Wait for Service Readiness') {
      steps {
        script {
          timeout(time: 1, unit: 'MINUTES') {
            waitUntil {
              def response = sh(
                script: "curl -s -o /dev/null -w '%{http_code}' http://host.docker.internal:$PORT/docs || true",
                returnStdout: true
              ).trim()
              echo "Health check response: $response"
              return (response == "200")
            }
          }
        }
      }
    }

    stage('Valid Inference Test') {
      steps {
        script {
          def response = sh(
            script: "curl -s -X POST http://host.docker.internal:$PORT/predict -H 'Content-Type: application/json' -d @tests/valid_input.json",
            returnStdout: true
          ).trim()
          echo "Valid Response: ${response}"
          if (!response.contains("wine_quality")) {
            error("Prediction field 'wine_quality' missing!")
          }
          def json = readJSON text: response
          def quality = json.wine_quality
          if (quality == null || !quality.toString().matches(/^-?\\d+$/)) {
            error("Prediction value is not numeric: ${quality}")
          }
          echo "Validation passed: wine_quality=${quality}"
        }
      }
    }

    stage('Invalid Inference Test') {
      steps {
        script {
          def response = sh(
            script: "curl -s -o /dev/null -w '%{http_code}' -X POST http://host.docker.internal:$PORT/predict -H 'Content-Type: application/json' -d @tests/invalid_input.json",
            returnStdout: true
          ).trim()
          echo "Invalid Request HTTP Code: ${response}"
          if (response == "200") {
            error("Invalid request did not fail! API should return error for malformed input.")
          }
          echo "Invalid request correctly rejected with HTTP ${response}"
        }
      }
    }

    stage('Stop Container') {
      steps {
        sh """
          docker stop $CONTAINER_NAME || true
          docker rm $CONTAINER_NAME || true
        """
      }
    }

  }

  post {
    always {
      sh "docker stop $CONTAINER_NAME || true"
      sh "docker rm $CONTAINER_NAME || true"
    }
  }
}
