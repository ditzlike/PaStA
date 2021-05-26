#!/usr/bin/bash

project=$(cat config)
tags=$(git -C resources/$project/repo tag --list | grep -v "v2.6")

RES="resources/$project/resources"
CLSTRS=$RES/maintainers_cluster

mkdir -p $CLSTRS

for tag in $tags; do
	if [ -f $CLSTRS/$tag.txt ]; then
		echo "Skipping $tag: already existing"
		continue
	fi
	./pasta maintainers_stats --mode graph --revision $tag
	mv $RES/maintainers_clusters.txt $CLSTRS/${tag}.txt
done
