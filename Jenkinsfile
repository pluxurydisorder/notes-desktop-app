pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    environment {
        APP_IMAGE = 'notes-web'
        APP_CONTAINER = 'notes-web'
        APP_PORT = '8081'
        APP_INTERNAL_PORT = '5000'
        APP_VOLUME = 'notes-web-data'
        // Common Docker CLI paths on Apple Silicon and Intel macOS.
        PATH+DOCKER = '/Users/sorrow/.docker/bin:/opt/homebrew/bin:/usr/local/bin:/opt/homebrew/sbin'
    }

    stages {
        stage('Checkout source from GitHub') {
            steps {
                checkout scm
                sh '''
                    set -eu
                    echo "Checked out commit: $(git rev-parse --short HEAD)"
                    test -f Dockerfile
                    test -f practice2_notes/app.py
                    test -f practice2_notes/requirements.txt
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    set -eu
                    docker version
                    docker build --pull --file Dockerfile \
                        --tag "$APP_IMAGE:$BUILD_NUMBER" .
                    docker tag "$APP_IMAGE:$BUILD_NUMBER" "$APP_IMAGE:latest"
                '''
            }
        }

        stage('Deploy container') {
            steps {
                sh '''
                    set -eu
                    docker volume create "$APP_VOLUME" >/dev/null

                    if docker container inspect "$APP_CONTAINER" >/dev/null 2>&1; then
                        docker stop "$APP_CONTAINER" >/dev/null 2>&1 || true
                        docker rm "$APP_CONTAINER" >/dev/null
                    fi

                    docker run --detach \
                        --name "$APP_CONTAINER" \
                        --restart unless-stopped \
                        --label "managed-by=jenkins" \
                        --publish "127.0.0.1:$APP_PORT:$APP_INTERNAL_PORT" \
                        --env "NOTES_DATABASE=/data/notes.db" \
                        --env "FLASK_SECRET_KEY=${FLASK_SECRET_KEY:-practice4-local-demo-key-change-me}" \
                        --volume "$APP_VOLUME:/data" \
                        "$APP_IMAGE:$BUILD_NUMBER"
                '''
            }
        }

        stage('Verify deployed application') {
            steps {
                sh '''
                    set -eu
                    attempt=1
                    while [ "$attempt" -le 20 ]; do
                        if curl --silent --show-error --fail "http://127.0.0.1:$APP_PORT/" >/dev/null; then
                            echo "Application is responding at http://127.0.0.1:$APP_PORT/"
                            exit 0
                        fi
                        sleep 2
                        attempt=$((attempt + 1))
                    done

                    echo "Application did not become ready. Container logs:"
                    docker logs "$APP_CONTAINER" || true
                    exit 1
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed: source checked out, Docker image built, container deployed.'
            echo 'Open http://127.0.0.1:8081/ to use the Notes web app.'
        }
        failure {
            sh 'docker logs "$APP_CONTAINER" || true'
            echo 'Pipeline failed. Review the log of the failed stage above.'
        }
    }
}
