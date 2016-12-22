//-*- mode: groovy; -*-

node ('slave04 || slave05') {

     stage('Checkout') {
        checkout scm
     }

     // buggy pyvenv-3.4 apparently doesn't add an activate script so we do the long winded way
     def workspace = pwd()
     def venv = "${workspace}/pvenv"
     stage('Setup venv') {
       def exists = fileExists venv
       if (!exists) {
         sh """pyvenv-3.4 --without-pip ${venv}
               source ${venv}/bin/activate
               curl https://bootstrap.pypa.io/get-pip.py | python
               deactivate
               source ${venv}/bin/activate
            """
       }
       // requirements might change
       sh """
          source ${venv}/bin/activate
          cd ${workspace}
          pip install -e .[test] --upgrade
          """
     }


     stage('Run tests') {
       sh """
          cd ${workspace}
          source ${venv}/bin/activate
          cd tests && python test_client.py
          """
     }
}
