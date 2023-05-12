Prerequisites:

-   Download the `LazyFox` binary from this [repository](https://github.com/TimGarrels/LazyFox), and save it in the working directory `workflow/scripts`.

As mentioned in the LazyFox [paper](https://peerj.com/articles/cs-1291/), running LazyFox with a queue size of 1 and a thread count of 1 is equivalent to running the original FOX algorithm.

Expand All
@@ -163,7 +163,7 @@ rm -r temp
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/fox-int-module-list.txt ../../../static/networks_modules/OS-CX/int-edge-list-node-mapping.pickle ../../../static/networks_modules/OS-CX fox

```

Output: `fox-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`

#### 2. Detecting Modules via DEMON

Expand All
	@@ -180,7 +180,7 @@ python module_detection/detect-modules-via-demon.py ../../../static/networks_mod
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/demon-int-module-list.csv ../../../static/networks_modules/OS-CX/networkx-node-mapping.pickle ../../../static/networks_modules/OS-CX demon
```

Output: `demon-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`

#### 3. Detecting Modules via COACH

Expand All
@@ -197,20 +197,21 @@ python module_detection/detect-modules-via-coach.py ../../../static/networks_mod
python module_util/restore-node-labels-in-modules.py ../../../static/networks_modules/OS-CX/coach-int-module-list.csv ../../../static/networks_modules/OS-CX/networkx-node-mapping.pickle ../../../static/networks_modules/OS-CX coach

```

Output: `coach-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`

#### 4. Detecting Modules via ClusterONE

Paper: https://www.nature.com/articles/nmeth.1938

Prerequisites:

-   Download the ClusterONE JAR file from this [link](https://paccanarolab.org/static_content/clusterone/cluster_one-1.0.jar), and save it in the working directory `workflow/scripts`.

-   The source code of ClusterONE is also hosted at [GitHub](https://github.com/ntamas/cl1).

```

java -jar module_detection/cluster_one-1.0.jar --output-format csv ../../../static/networks/OS-CX.txt > ../../../static/networks_modules/OS-CX/clusterone-results.csv
python module_util/get-modules-from-clusterone-results.py ../../../static/networks_modules/OS-CX/clusterone-results.csv ../../../static/networks_modules/OS-CX

```

Output: `clusterone-module-list.txt` in `../../../static/networks_modules/OS-CX/module_list`
```
