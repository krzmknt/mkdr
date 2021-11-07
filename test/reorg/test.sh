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


#------------------------------------------------------------------------------#
# Initialize
#------------------------------------------------------------------------------#
set -u
THIS_DIR=$(cd $(dirname $0); pwd)
cd $THIS_DIR

cd ../
cp -r reorg reorg_bk_ver
cd reorg

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
NAME='Reorg - Basic Reorganization'
python $MKDR -r &> out-reorg
diff out-reorg check/out-reorg &> out-diff
FILE=out-diff
checkEmpty
rm out* &> /dev/null

tree &> out-tree
diff out-tree check/out-tree &> out-diff
FILE=out-diff
checkEmpty

cat dir/1/file &> out-file1
diff out-file1 check/out-file1 &> out-diff
file=out-diff
checkEmpty

cat dir/2/file &> out-file2
diff out-file2 check/out-file2 &> out-diff
FILE=out-diff
checkEmpty

cat dir/3/file &> out-file3
diff out-file3 check/out-file3 &> out-diff
FILE=out-diff
checkEmpty

#------------------------------------------------------------------------------#
# Postprocess
#------------------------------------------------------------------------------#
cd ../
rm -r reorg
cp -r reorg_bk_ver reorg
rm -r reorg_bk_ver

echo $RC

