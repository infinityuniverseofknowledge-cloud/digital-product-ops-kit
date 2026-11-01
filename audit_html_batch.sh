#!/data/data/com.termux/files/usr/bin/bash
# Review-first static HTML inventory for Termux or Linux.
# Usage: bash audit_html_batch.sh path/to/projects output
set -eu
SOURCE=$1
OUT=${2:-output}
mkdir -p $OUT
CSV=$OUT/catalog.csv
REPORT=$OUT/release-gate.md
printf path,title,bytes,has_form,external_scripts,credential_marker\n > $CSV
printf #\ Release\ Gate\n\n > $REPORT
printf This\ report\ is\ a\ review\ queue\ and\ not\ publication\ approval.\n\n >> $REPORT
find $SOURCE -type f -name \*.html -print | sort | while IFS= read -r FILE
do
  NAME=${FILE#$SOURCE/}
  SIZE=$(wc -c < $FILE | tr -d ' ')
  TITLE=$(tr '\n' ' ' < $FILE | sed -n 's:.*<title[^>]*>\(.*\)</title>.*:\1:Ip' | sed 's/<[^>]*>//g' | head -c 160)
  FORM=no
  grep -qiE '<form[[:space:]>]' $FILE && FORM=yes || true
  REMOTE=$(grep -Eio '<script[^>]+src=[^ >]+' $FILE | grep -Eic 'http|//' || true)
  RISK=no
  grep -qiE 'api[_-]?key|secret|private[_-]?key|password[[:space:]]*[:=]|seed[[:space:]]+phrase' $FILE && RISK=yes || true
  printf %s,%s,%s,%s,%s,%s\n $NAME $TITLE $SIZE $FORM $REMOTE $RISK >> $CSV
  if [ -z $TITLE ] || [ $FORM = yes ] || [ $REMOTE -gt 0 ] || [ $RISK = yes ]
  then
    printf %s\n $NAME >> $REPORT
    [ -z $TITLE ] && printf -- '- [ ] Add an accurate page title\n' >> $REPORT || true
    [ $FORM = yes ] && printf -- '- [ ] Review form privacy and functionality\n' >> $REPORT || true
    [ $REMOTE -gt 0 ] && printf -- '- [ ] Document and test remote scripts\n' >> $REPORT || true
    [ $RISK = yes ] && printf -- '- [ ] BLOCKER review credential-like text\n' >> $REPORT || true
    printf \n >> $REPORT
  fi
done
printf Catalog\ created:\ %s\n $CSV
printf Review\ queue:\ %s\n $REPORT
