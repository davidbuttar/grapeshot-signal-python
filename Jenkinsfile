//-*- mode: groovy; -*-

node ('slave04 || slave05') {

     stage('Checkout') {
        checkout scm
     }

     stage('Setup venv') {
       sh '''PATH=$WORKSPACE/venv/bin:$PATH
             if [ ! -d "venv" ]; then
                   pyvenv venv
             fi
             . venv/bin/activate
             pip install -r requirements.txt --download-cache=/tmp/$JOB_NAME
             '''
     }

     stage('Run tests') {
       sh 'cd tests && python test_client.py'
     }
}
