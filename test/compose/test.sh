#!bin/bash


#------------------------------------------------------------------------------#
# Check Function
#------------------------------------------------------------------------------#
function checkEmpty(){
  if [ ! -s $FILE ]; then
    echo Success: $NAME >> log
  else
    echo Error: $NAME >> log
    RC=0
  fi
}

function checkDate(){
  if [ $DATE1 == $DATE2 ]; then
    echo Success: $NAME >> log
  else
    echo Error: $NAME >> log
    RC=0
  fi
}

#------------------------------------------------------------------------------#
# Initialize
#------------------------------------------------------------------------------#
set -u
THIS_DIR=$(cd $(dirname $0); pwd)
cd $THIS_DIR

rm out* &> /dev/null
rm log &> /dev/null


#------------------------------------------------------------------------------#
# Variable
#------------------------------------------------------------------------------#
MKDR='../../mkdr.py'
RC=1

#------------------------------------------------------------------------------#
# Basic Compose
#------------------------------------------------------------------------------#
NAME='Basic compose - no option'
python $MKDR &> out-compose
diff out-compose check/out-compose &> out-diff
FILE=out-diff
checkEmpty
rm out*
python $MKDR -df &> /dev/null

NAME='Basic compose --compose'
python $MKDR --compose &> out-compose
diff out-compose check/out-compose &> out-diff
FILE=out-diff
checkEmpty
rm out*
python $MKDR -df &> /dev/null

NAME='Basic compose -c'
python $MKDR -c &> out-compose
diff out-compose check/out-compose &> out-diff
FILE=out-diff
checkEmpty


#------------------------------------------------------------------------------#
# Template
#------------------------------------------------------------------------------#
NAME='template will be used'
diff .mkdr/template.html dir/a/a/a/index.html &> out-diff
FILE=out-diff
checkEmpty

NAME='template will not be used'
FILE='dir/test.md'
checkEmpty


#------------------------------------------------------------------------------#
# Timestamp
#------------------------------------------------------------------------------#
DATETEMP=$(date -r .mkdr/template.html '+%Y%m%d%H')
DATENOW=$(date '+%Y%m%d%H')

NAME=timestamp-html
DATE1=$(date -r dir/a/a/a/index.html '+%Y%m%d%H')
DATE2=$DATENOW
checkDate

NAME=timestamp-not-exist
DATE1=$(date -r 'dir/test.md' '+%Y%m%d%H')
DATE2=$DATENOW
checkDate




#------------------------------------------------------------------------------#
# Postprocess
#------------------------------------------------------------------------------#
rm out* &> /dev/null
python $MKDR -df &> /dev/null
echo $RC

