#!/bin/bash
if [ $# -lt 1 ] ; then
  echo "Usage: $0 <serialID>"
  exit
fi

for i in *.py; do
  echo "Running $i ..."
  ./$i $1 
  echo "Press Enter to continue, or type q to quit"
  read text
  if [ "$text" == "q" ] ; then
    exit
  fi
  sleep 1
done
