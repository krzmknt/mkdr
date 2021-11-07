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
# Reorg
#------------------------------------------------------------------------------#
NAME='Reorg - Do not exchange anything - succesffully terminated'
python $MKDR --reorg &> out-reorg
diff out-reorg check/out-reorg &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null

NAME='Reorg - Do not exchange anything - Nothing have been changed.'
tree &> out-tree
diff out-tree check/out-tree &> out-diff
FILE=out-diff
checkEmpty

cat file &> out-file1
diff out-file1 check/out-file1 &> out-diff
file=out-diff
checkEmpty

cat dir/file &> out-file2
diff out-file2 check/out-file2 &> out-diff
FILE=out-diff
checkEmpty

cat dir/dir/file &> out-file3
diff out-file3 check/out-file3 &> out-diff
FILE=out-diff
checkEmpty

#------------------------------------------------------------------------------#
# Postprocess
#------------------------------------------------------------------------------#
rm out* &> /dev/null
touch dir/test
echo $RC

