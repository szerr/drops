outpath=../replase

while getopts ":o:" opt; do
  case $opt in
    o)
      outpath=$OPTARG
      ;;
    ?) 
      echo "Invalid option: -$OPTARG index:$OPTIND"
      ;;

  esac
done

cp ../index.html $outpath