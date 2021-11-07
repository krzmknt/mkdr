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
# Export
#------------------------------------------------------------------------------#
NAME='Export --export'
python $MKDR --export &> out-export
diff out-export check/out-export &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null

NAME='The exported beakfile name is mkdrcompose.yml'
FILE='mkdrcompose.yml'
checkExistence

NAME='The validity of the contents of mkdrcompose.yml'
diff mkdrcompose.yml check/mkdrcompose.yml &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null
rm 'mkdrcompose.yml' &> /dev/null

NAME='Export -e'
python $MKDR -e &> out-export
diff out-export check/out-export &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null
rm 'mkdrcompose.yml' &> /dev/null


#------------------------------------------------------------------------------#
# Postprocess
#------------------------------------------------------------------------------#
rm out* &> /dev/null
echo $RC

