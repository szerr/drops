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
# 如果遇到错误，记得 exit 非0，让上层逻辑停止。
exit 0 