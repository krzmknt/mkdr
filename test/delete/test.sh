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

function checkExistence(){
  if [ -e $FILE ]; then
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
# Delete
#------------------------------------------------------------------------------#
NAME='--delete'
python $MKDR --delete --force &> out-delete
diff out-delete check/out-delete &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null

NAME='Check that objects have been deleted.'
ls &> out-ls
diff out-ls check/out-ls &> out-diff
FILE=out-diff
checkEmpty
python $MKDR &> out-compose


NAME='-d'
python $MKDR -df &> out-delete
diff out-delete check/out-delete &> out-diff
FILE=out-diff
checkEmpty
python $MKDR &> out-compose


#------------------------------------------------------------------------------#
# Postprocess
#------------------------------------------------------------------------------#
rm out* &> /dev/null
echo $RC

