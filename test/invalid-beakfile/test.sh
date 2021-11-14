#!bin/bash


#------------------------------------------------------------------------------#
# Check Function
#------------------------------------------------------------------------------#
function checkEmpty(){
  if [ ! -s $FILE ]; then
    echo Success: $NAME >> out/log
  else
    echo Error: $NAME >> out/log
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
NAME='Invalid beakfile'
python $MKDR &> out/out-error
diff out/out-error check/out-error &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null


NAME='Empty beakfile'
python $MKDR -n empty &> out/out-empty
diff out/out-empty check/out-empty &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null


#------------------------------------------------------------------------------#
# Postprocess
#------------------------------------------------------------------------------#
rm out* &> /dev/null
echo $RC

