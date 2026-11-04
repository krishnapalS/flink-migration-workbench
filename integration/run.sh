#!/usr/bin/env sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$ROOT"
python -m migration examples/orders.xml --out build/demo
mvn -q -f integration/pom.xml compile dependency:build-classpath -Dmdep.outputFile="$ROOT/integration/target/classpath.txt"
java -cp "$ROOT/integration/target/classes:$(cat integration/target/classpath.txt)" RuntimeCheck "$ROOT/build/demo/mapping.sql"
