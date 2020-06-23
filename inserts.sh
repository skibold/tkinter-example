#! /bin/bash

rm -f auth_inserts.sql 2>/dev/null
rm -f book_inserts.sql 2>/dev/null
rm -f book_auth_inserts.sql 2>/dev/null

rep="\\\'"
cut books.csv -f1 > isbns.txt
cut books.csv -f3 | sed "s/'/"$rep"/g" > titles.txt
cut books.csv -f4 | sed "s/'/"$rep"/g" > authors.txt

linenum=0
while read isbn
do
	((linenum++))
	[[ $linenum -eq 1 ]] && continue # skip first line header

	title=$(sed "$linenum"','"$linenum"'!d' titles.txt)
	echo "insert into book (isbn, title) values ('$isbn', '$title');" >> book_inserts.sql

	ifssave=$IFS
	IFS=,
	authors=($(sed "$linenum"','"$linenum"'!d' authors.txt))
	IFS=$ifssave
	for ((a=0; a<${#authors[@]}; a++))
	do
		echo "insert into authors (name) values ('${authors[$a]}');" >> auth_inserts.sql
		echo "insert into book_authors (author_id, isbn) values ((select author_id from authors where name = '${authors[$a]}'), '$isbn');" >> book_auth_inserts.sql
	done
done < isbns.txt

rm -f borrower_inserts.sql 2>/dev/null
while read line
do
        [[ $(echo $line | cut -c 1) == "#" ]] && continue # skip comments
        id=$(echo $line | cut -d ',' -f 1)
        ssn=$(echo $line | cut -d ',' -f 2 | sed 's/-//g')
        name=$(echo $line | cut -d ',' -f 3-4 | tr ',' ' ')
        addr=$(echo $line | cut -d ',' -f 6-8)
        phone=$(echo $line | cut -d ',' -f 9)
        echo "insert into borrower (card_id, ssn, bname, address, phone) values ('$id', '$ssn', '$name', '$addr', '$phone');" >> borrower_inserts.sql
done < borrowers.csv
