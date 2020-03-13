@Library(['promebuilder', 'offconda'])_


pipeline {
  agent any
  parameters {
    string(
        name: 'COMPONENTS',
        description: 'Forced Final packages and version',
        defaultValue: ''
    )
    string(
        name: 'LABEL',
        defaultValue: env.TAG_NAME ? (env.TAG_NAME.contains('rc') ? 'release' : 'main') : env.BRANCH_NAME.split('/')[0].replace('master', 'main'),
        description: 'Source label'
    )
    string(
        name: 'TARGET',
        defaultValue: 'C:\\OFFCONDA',
        description: 'Target offline repository'
    )
    booleanParam(
        name: 'ASK_PUB_CONFIRM',
        defaultValue: true,
        description: "Wait for confirm before publishing"
    )
    booleanParam(
        name: 'ALL_VARIANTS',
        defaultValue: true,
        description: "Search for all packages variants"
    )
    booleanParam(
        name: 'CROSS_ORIGINS',
        defaultValue: false,
        description: "Search variants accross origins"
    )
  }
  environment {
    CONDAENV = "${env.JOB_NAME}_${env.BUILD_NUMBER}".replace('%2F','_').replace('/', '_')
  }
  stages {
    stage('Bootstrap') {
      steps {
        echo "NB: The packages should be PRIVATE o PUBLIC, it doesn't work with 'authentication required'."
        writeFile file: 'components.txt', text: (params.COMPONENTS ? params.COMPONENTS : readFile('versions.txt'))
        archiveArtifacts artifacts: "*.txt"
        stash(name: "source", useDefaultExcludes: true)
      }
    }
    stage("Packages Discovery") {
      parallel {
        stage("Target Linux") {
          steps {
            doublePackager('linux', params.LABEL, readFile("components.txt") + " " + readFile("linux.txt"))
          }
        }
        stage("Target Linux Legacy") {
          steps {
             doublePackager('linux-legacy', params.LABEL, readFile("components.txt") + " " + readFile("linux-legacy.txt"))
          }
        }
        stage("Target Windows") {
          steps {
            doublePackager('windows', params.LABEL, readFile("components.txt") + " " + readFile("windows.txt"))
          }
        }
      }
    }

    stage('Packages Downloading and Indexing') {
      when {
        buildingTag()
      }
      steps {
        unarchive(mapping: ["elencone-linux.txt": "elencone-linux.txt", "elencone-windows.txt": "elencone-windows.txt", "elencone-linux-legacy.txt": "elencone-linux-legacy.txt"])
        script {
          try {
            bat(script: "del ${env.TAG_NAME}\\*.* /S /Q")
            bat(script: "RMDIR ${env.TAG_NAME} /S")
          } catch (err) {
            echo err.getMessage()
          }
          if (params.ALL_VARIANTS) {
            if (params.CROSS_ORIGINS) {
              bat(script: "python download.py -o ${env.TAG_NAME} --allvariants --crossorigins")
            } else {
              bat(script: "python download.py -o ${env.TAG_NAME} --allvariants")
            }
          } else {
            bat(script: "python download.py -o ${env.TAG_NAME}")
          }
        }
        bat(script: "call conda index ${env.TAG_NAME}")
      }
    }
    stage('Checking Distribution') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "python distrocheck.py ${env.TAG_NAME}")
        archiveArtifacts artifacts: "${env.TAG_NAME}/*/*.json"
      }
    }

    stage ('Distribution publish confirm') {
      when {
        allOf {
          buildingTag()
          expression { return params.ASK_PUB_CONFIRM }
        }
      }
      steps {
        timeout(time: 24, unit: "HOURS") {
          input(message: "Ready to publish the distributions?", ok: "OK, publish now!")
        }
      }
    }

    stage('Publishing Distribution') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "(robocopy /MIR ${env.TAG_NAME} ${params.TARGET}\\${env.TAG_NAME} /XD ${env.TAG_NAME}\\win-64\\.cache ${env.TAG_NAME}\\linux-64\\.cache ${env.TAG_NAME}\\noarch\\.cache ) ^& IF %ERRORLEVEL% LEQ 1 exit 0")
      }
    }
    stage('Testing Distribution') {
      when {
        buildingTag()
      }
      steps {
        bat(script: "conda install pytho ratingpro " + readFile("windows.txt") + " --offline -c ${params.TARGET}\\${env.TAG_NAME} --override-channels --dry-run")
        script {
          try {
            node('linux') {
              unarchive(mapping: ["components.txt": "components.txt", "linux.txt": "linux.txt"])
              sh(script: "conda install " + readFile("components.txt") + " " + + readFile("linux.txt") + " -c ${env.DELIVERY_URL}/${env.TAG_NAME} --override-channels --dry-run")
            }
          } catch (Exception e) {
            echo "Linux test crashed"
          }
        }
      }
    }
  }
  post {
    success {
      slackSend color: "good", message: "Successed ${env.JOB_NAME} (<${env.BUILD_URL}|Open>)"
      deleteDir()
    }
    failure {
      slackSend color: "warning", message: "Failed ${env.JOB_NAME} (<${env.BUILD_URL}|Open>)"
    }
  }
}
