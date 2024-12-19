scripts/module_detection/LazyFox --input-graph $1 --output-dir scripts/temp --queue-size 20 --thread-count 20 --disable-dumping --wcc-threshold $2
mv scripts/temp/CPP*/iterations/*.txt $3
rm -r scripts/temp