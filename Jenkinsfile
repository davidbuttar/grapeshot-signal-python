//-*- mode: groovy; -*-

node ('slave04 || slave05') {

     stage('Checkout') {
        checkout scm
     }

     // buggy pyvenv-3.4 apparently doesn't add an activate script so we do the long winded way
     def workspace = pwd()
     stage('Setup venv') {
       def exists = fileExists 'venv'
       if (!exists) {
         sh """pyvenv-3.4 --without-pip ${workspace}/venv
               source ${workspace}/venv/bin/activate
               curl https://bootstrap.pypa.io/get-pip.py | python
               deactivate
               source ${workspace}/venv/bin/activate
            """
       }
       // requirements might change
       sh """
          source ${workspace}/venv/bin/activate
          pip install -r requirements.txt --upgrade --download-cache=/tmp/${env.JOB_NAME}
          """
     }


     stage('Run tests') {
       sh """
          source ${workspace}/venv/bin/activate
          cd tests && python test_client.py
          """
     }
}
