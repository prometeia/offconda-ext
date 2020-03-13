getversion() {
    git archive --format=tar master version | tar -xO
}


escrow() {
    local PROD=$1
    local SUBPATH=$2
    if [ -z "$SUBPATH" ]; then 
        SUBPATH=$PROD
    fi
    cd $PROD
    local VER="$(getversion)"    
    git fetch
    local FNAME="$PROD-$VER.zip"
    echo "Building source repo for $PROD v$VER in $FNAME"
    git archive -o ../$FNAME --prefix $PROD/ master:$SUBPATH
    cd ..
    echo "Done!"
}


escrow "pytho"
escrow "gsf" "commonlib/gsf"
escrow "ratingpro"
escrow "pkgateway"
