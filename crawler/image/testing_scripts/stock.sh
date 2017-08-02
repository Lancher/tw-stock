#!/usr/bin/env bash

source /etc/environment
source /etc/profile

DATE=$(TZ='Asia/Taipei' date +%Y-%m-%d)

SCRIPTS_DIR=/testing_scripts
BROKERS_SCRIPT_DIR=${SCRIPTS_DIR}/selenium-grep-brokers
TSE_SCRIPT_DIR=${SCRIPTS_DIR}/selenium-grep-tse-reports
OTC_SCRIPT_DIR=${SCRIPTS_DIR}/selenium-grep-otc-reports
CMONEY_SCRIPT_DIR=${SCRIPTS_DIR}/selenium-grep-cmoney
LOG=${SCRIPTS_DIR}/stock.txt

EMAIL_SENDER=stock@stock.c.cobalt-cider-169103.internal
EMAIL_RECEIVER=steve.liushihao@gmail.com

function email_start {
  if [ -n "${EMAIL_SENDER}" ]; then
    echo "email start"
    echo "Hi, stock data starts at $(TZ='Asia/Taipei' date +%Y-%m-%d:%H:%M:%S)." | mailx -s "${DATE} Stock Daily Report: Start to download!" -r "${EMAIL_SENDER}" "${EMAIL_RECEIVER}"
  else
    echo "email start not sent"
  fi
}

function email_success {
  if [ -n "${EMAIL_SENDER}" ]; then
    echo "email success"
    echo "Hi, stock data succeed at $(TZ='Asia/Taipei' date +%Y-%m-%d:%H:%M:%S)." | mailx -s "${DATE} Stock Daily Report: Success!" -r "${EMAIL_SENDER}" "${EMAIL_RECEIVER}" -A "${LOG}"
  else
    echo "email success not sent"
  fi
}

function email_error {
  if [ -n "${EMAIL_SENDER}" ]; then
    echo "email error"
    echo "Hi, stock data failed because of $1 at $(TZ='Asia/Taipei' date +%Y-%m-%d:%H:%M:%S)." | mailx -s "${DATE} Stock Daily Report: Error!" -r "${EMAIL_SENDER}" "${EMAIL_RECEIVER}" -A "${LOG}"
  else
    echo "email error not sent"
  fi
}

email_start

# grep brokers
cd ${BROKERS_SCRIPT_DIR}
TZ='Asia/Taipei' DISPLAY=:1 ./run.py
rc=$?; if [[ $rc != 0 ]]; then email_error "greping brokers"; exit $rc; fi

# grep tse companies
cd ${TSE_SCRIPT_DIR}
TZ='Asia/Taipei' DISPLAY=:1 ./run.py
rc=$?; if [[ $rc != 0 ]]; then email_error "greping tse companies"; exit $rc; fi

# grep otc companies
cd ${OTC_SCRIPT_DIR}
TZ='Asia/Taipei' DISPLAY=:1 ./run.py
rc=$?; if [[ $rc != 0 ]]; then email_error "greping otc companies"; exit $rc; fi

# grep cmoney
cd ${CMONEY_SCRIPT_DIR}
TZ='Asia/Taipei' DISPLAY=:1 ./run.py
rc=$?; if [[ $rc != 0 ]]; then  email_error "greping cmoney"; exit $rc; fi

email_success

