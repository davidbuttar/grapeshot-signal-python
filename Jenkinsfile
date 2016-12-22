//-*- mode: groovy; -*-

node ('slave04 || slave05') {

     stage('Checkout') {
        checkout scm
     }


     stage('Setup venv') {
       def exists = fileExists 'venv'
       if (!exists) {
         sh "pyvenv venv"
       }
       sh """
          . venv/bin/activate
          pip install -r requirements.txt --download-cache=/tmp/${env.JOB_NAME}
          """
     }


     stage('Run tests') {
       sh """
          . venv/bin/activate
          cd tests && python test_client.py
          """
     }
}
