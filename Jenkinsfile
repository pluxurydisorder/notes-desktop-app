pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
        disableConcurrentBuilds()
    }

    parameters {
    string(
        name: 'DEPLOY_HOST',
        defaultValue: '192.168.64.2',
        description: 'IP-адрес Ubuntu-сервера в UTM'
    )
}

    environment {
        // Use a normal PATH assignment; PATH+NAME inside environment can fail
        // to parse on some Jenkins versions.
        PATH = "/Users/sorrow/.docker/bin:/opt/homebrew/bin:/usr/local/bin:/opt/homebrew/sbin:${env.PATH}"
        APP_IMAGE = 'notes-web'
        APP_CONTAINER = 'notes-web'
        APP_VOLUME = 'notes-web-data'
        APP_HOST_PORT = '8081'
        APP_CONTAINER_PORT = '5000'
    }

    stages {
        stage('Checkout source and deployment playbook') {
            steps {
                checkout scm
                sh '''
                    set -eu
                    echo "Checked out commit: $(git rev-parse --short HEAD)"
                    test -f Dockerfile
                    test -f Jenkinsfile
                    test -f practice2_notes/app.py
                    test -f practice2_notes/requirements.txt
                    test -f ansible/deploy-container.yml
                    echo "Dockerfile and Ansible playbook are present in the GitHub checkout."
                '''
            }
        }

        stage('Build Docker image') {
            steps {
                sh '''
                    set -eu
                    command -v docker
                    docker version
                    # The Mac M1 and the Ubuntu ARM64 VM both use linux/arm64.
                    docker build --platform linux/arm64 --pull \
                        --file Dockerfile \
                        --tag "$APP_IMAGE:$BUILD_NUMBER" .
                    docker tag "$APP_IMAGE:$BUILD_NUMBER" "$APP_IMAGE:latest"
                '''
            }
        }

        stage('Export Docker image') {
            steps {
                sh '''
                    set -eu
                    docker save --output "$WORKSPACE/$APP_IMAGE-$BUILD_NUMBER.tar" \
                        "$APP_IMAGE:$BUILD_NUMBER"
                    ls -lh "$WORKSPACE/$APP_IMAGE-$BUILD_NUMBER.tar"
                    shasum -a 256 "$WORKSPACE/$APP_IMAGE-$BUILD_NUMBER.tar"
                '''
            }
        }

        stage('Deploy image to Ubuntu with Ansible') {
            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: 'notes-ubuntu-ssh',
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USER'
                    ),
                    string(
                        credentialsId: 'notes-ubuntu-sudo-password',
                        variable: 'ANSIBLE_BECOME_PASSWORD'
                    )
                ]) {
                    sh '''
                        set -eu
                        set +x
                        command -v ansible-playbook
                        test -r "$SSH_KEY"
                        test -s "$WORKSPACE/$APP_IMAGE-$BUILD_NUMBER.tar"

                        # Validate the parameter before writing it into inventory.
                        case "$DEPLOY_HOST" in
                            ""|*[!-A-Za-z0-9._:]* )
                                echo "Invalid DEPLOY_HOST. Use an IP address or hostname."
                                exit 2
                                ;;
                        esac

                        mkdir -p "$HOME/.ssh"
                        chmod 700 "$HOME/.ssh"
                        touch "$HOME/.ssh/known_hosts"
                        chmod 600 "$HOME/.ssh/known_hosts"
                        if ! ssh-keygen -F "$DEPLOY_HOST" -f "$HOME/.ssh/known_hosts" >/dev/null 2>&1; then
                            # For this local teaching VM, add the SSH host key once.
                            # In production, verify the fingerprint out-of-band first.
                            ssh-keyscan -H "$DEPLOY_HOST" >> "$HOME/.ssh/known_hosts" 2>/dev/null
                        fi

                        cat > "$WORKSPACE/.jenkins-inventory.ini" <<EOF_INVENTORY
[web]
notes-server ansible_host=$DEPLOY_HOST ansible_user=$SSH_USER ansible_python_interpreter=/usr/bin/python3
EOF_INVENTORY

                        BECOME_PASSWORD_FILE="$WORKSPACE/.ansible-become-pass"
                        trap 'rm -f "$BECOME_PASSWORD_FILE"' EXIT
                        printf '%s' "$ANSIBLE_BECOME_PASSWORD" > "$BECOME_PASSWORD_FILE"
                        chmod 600 "$BECOME_PASSWORD_FILE"

                        ansible-playbook \
                            --inventory "$WORKSPACE/.jenkins-inventory.ini" \
                            --private-key "$SSH_KEY" \
                            --become-password-file "$BECOME_PASSWORD_FILE" \
                            "$WORKSPACE/ansible/deploy-container.yml" \
                            --extra-vars "image_name=$APP_IMAGE image_tag=$BUILD_NUMBER image_archive=$WORKSPACE/$APP_IMAGE-$BUILD_NUMBER.tar container_name=$APP_CONTAINER host_port=$APP_HOST_PORT container_port=$APP_CONTAINER_PORT app_volume=$APP_VOLUME"
                    '''
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed: source checked out, Docker image built and transferred, remote container deployed and checked.'
            echo "Open the deployed app at http://${params.DEPLOY_HOST}:8081/ (if the VM network allows host-to-guest access)."
        }
        failure {
            echo 'Pipeline failed. Open Console Output and inspect the first failed stage.'
        }
        always {
            sh '''
                rm -f "$WORKSPACE/$APP_IMAGE-$BUILD_NUMBER.tar" \
                      "$WORKSPACE/.jenkins-inventory.ini" \
                      "$WORKSPACE/.ansible-become-pass" || true
            '''
        }
    }
}
