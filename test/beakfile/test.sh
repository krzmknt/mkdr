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
# Beakfile
#------------------------------------------------------------------------------#
NAME='--name'
python $MKDR --name a &> /dev/null
tree &> out-compose
diff out-compose check/out-compose &> out-diff
FILE=out-diff
checkEmpty

NAME='-n'
python $MKDR -dfn a &> /dev/null
tree &> out-delete
diff out-delete check/out-delete &> out-diff
FILE=out-diff
checkEmpty


#------------------------------------------------------------------------------#
# Postprocess
#------------------------------------------------------------------------------#
rm out* &> /dev/null
echo $RC

