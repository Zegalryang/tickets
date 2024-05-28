#!/bin/bash

#https://googlechromelabs.github.io/chrome-for-testing/#stable
# mac osx https://storage.googleapis.com/chrome-for-testing-public/125.0.6422.78/mac-x64/chromedriver-mac-x64.zip

OS=$(uname)
FINALPATH=

if [[ $OS == "Linux" ]]; then
    FINALPATH=chromedriver-linux64
    VERSION=$(google-chrome --version | awk '{print $3;}')
    curl -O https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/linux64/${FINALPATH}.zip
else
    FINALPATH=chromedriver-mac-x64
    curl -O https://storage.googleapis.com/chrome-for-testing-public/${VERSION}/mac-x64/${FINALPATH}.zip
fi

if test -z ${FINALPATH}; then
    echo "No chromedriver retrieved"
    exit 1
fi

unzip ${FINALPATH}.zip
mv ${FINALPATH}/chromedriver .
rm -rf ${FINALPATH}*

echo "done."
