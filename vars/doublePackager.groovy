#!/usr/bin/env groovy

def call(envlabel, sourcelabel, components, condaenvb="base") {
  node(envlabel) {
    pipeline {
      stage('Unstash') {
        unstash "source"
      }
      stage('Generating packages list') {
        condaShellCmd("conda create -y -n ${CONDAENV}-${envlabel} python=2.7", condaenvb)
        retry(3) {
            condaShellCmd("conda install --copy -q -c t/${env.ANACONDA_API_TOKEN}/prometeia/channel/${sourcelabel} -c t/${env.ANACONDA_API_TOKEN}/prometeia -c defaults --override-channels -y ${components}", "${CONDAENV}-${envlabel}")
        }
        script {
          writeFile file: "elencone-${envlabel}.txt", text: condaShellCmd("conda list --explicit", "${CONDAENV}-${envlabel}", true).trim()
        }
      }
      stage('ArtifactTearDown') {
        archiveArtifacts artifacts: "elencone-${envlabel}.txt"
        condaShellCmd("conda env remove -y -n ${CONDAENV}-${envlabel}", condaenvb)
        deleteDir()
      }
    }
  }
}
