//-*- mode: groovy; -*-

node ('slave04 || slave05') {

     stage('Checkout') {
        checkout scm
     }

     withEnv(["WORKSPACE=${pwd()}"]) {

       stage('Setup venv') {

         sh """PATH=${env.WORKSPACE}/venv/bin:${env.PATH}
               if [ ! -d 'venv' ]; then
                     pyvenv venv
               fi
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
}
