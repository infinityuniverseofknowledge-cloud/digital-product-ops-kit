#!/bin/sh
# Review-first HTML inventory. Usage: sh audit_html_batch.sh SOURCE OUT
set -eu
SOURCE=$1
OUT=${2-output}
mkdir -p $OUT
CSV=$OUT/catalog.csv
REPORT=$OUT/release-gate.md
printf path,title,bytes,has_form,remote_script_count,credential_marker\n > $CSV
printf RELEASE_GATE\n\n > $REPORT
find $SOURCE -type f -name \*.html -print | sort | while read FILE
do
NAME=${FILE#$SOURCE/}
SIZE=$(wc -c < $FILE | tr -d ' ')
TITLE=$(tr '\n' ' ' < $FILE | sed -n 's:.*<title[^>]*>\(.*\)</title>.*:\1:Ip' | sed 's/<[^>]*>//g' | head -c 160)
FORM=no
grep -qi '<form' $FILE && FORM=yes || true
REMOTE=$(grep -Eic 'https?://|//[^ >]*' $FILE || true)
RISK=no
grep -qiE 'password|api_key|secret|private_key|seed phrase' $FILE && RISK=yes || true
printf %s,%s,%s,%s,%s,%s\n $NAME $TITLE $SIZE $FORM $REMOTE $RISK >> $CSV
if [ -z $TITLE ] || [ $FORM = yes ] || [ $REMOTE -gt 0 ] || [ $RISK = yes ]
then
printf %s\n $NAME >> $REPORT
[ -z $TITLE ] && printf MISSING_TITLE\n >> $REPORT || true
[ $FORM = yes ] && printf REVIEW_FORM_PRIVACY\n >> $REPORT || true
[ $REMOTE -gt 0 ] && printf REVIEW_REMOTE_SCRIPTS\n >> $REPORT || true
[ $RISK = yes ] && printf BLOCKER_CREDENTIAL_LIKE_TEXT\n >> $REPORT || true
printf \n >> $REPORT
fi
done
printf Catalog_created_at_%s\n $CSV
printf Review_queue_at_%s\n $REPORT
