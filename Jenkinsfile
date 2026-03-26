pipeline {
    agent any

    environment {
        // Получаем credentials из Jenkins
        PROD_BASE_URL = credentials('booker-prod-url')
        ENVIRONMENT = credentials('test-environment')

        // Для username/password - Jenkins автоматически создает две переменные
        // с суффиксами _USR и _PSW
        BOOKER_CREDS = credentials('booker-credentials')
        // После этой строки доступны:
        // BOOKER_CREDS_USR = 'admin'
        // BOOKER_CREDS_PSW = 'password123'
    }


    stages {
        stage('Setup Python Environment') {
            steps {
                // Шаг создания виртуального окружения и его активации
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate'

                // Установка зависимотей из requirements.txt
                sh 'pip install -r requirements.txt --break-system-packages'
            }
        }

        stage('Create .env File') {
            steps {
                sh '''
                    echo "=== Creating .env file from Jenkins credentials ==="
                    . venv/bin/activate

                    # Создаем .env файл с переменными
                    cat > .env << EOF
# Auto-generated from Jenkins credentials
ENVIRONMENT=${ENVIRONMENT}
PROD_BASE_URL=${PROD_BASE_URL}
TEST_BASE_URL=https://reqres.in/
BOOKER_USERNAME=${BOOKER_CREDS_USR}
BOOKER_PASSWORD=${BOOKER_CREDS_PSW}
EOF

                    # Проверяем что файл создался (но не показываем содержимое!)
                    echo ".env file created successfully"
                    ls -la .env
                '''
            }
        }

        stage('Run Tests') {
            steps {
                // Запуск тестов и генерация отчета allure
                sh 'python3 -m pytest --alluredir allure-results'
            }
        }

        stage('Generate Allure Report') {
            steps {
                // Публикация Allure отчетов (Если установлен плагин Allure)
                allure([
                    includeProperties: false,
                    jdk: '',
                    results: [[path: 'allure-results']]
                ])
            }
        }
    }

    post {
        always {
            // Сохранение отчетов о тестировании и любых других артефактов
            archiveArtifacts artifacts: '**/allure-results/**', allowEmptyArchive: true
        }
        failure {
            // Есди сборка провалилась, отправить уведомление или выполнить другое действие
            echo 'The build failed!'
        }
    }
}