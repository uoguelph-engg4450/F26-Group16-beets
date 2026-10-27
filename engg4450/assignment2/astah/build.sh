#!/usr/bin/env bash
# Builds the Assignment 2 use case diagram in Astah UML and exports it as PNG.
# usage: bash engg4450/assignment2/astah/build.sh
# Uses the headless runner and script-engine jars of Assignment 1 (engg4450/assignment1).
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
A2="$(dirname "$HERE")"
A1="$(dirname "$A2")/assignment1"
ASTAH_HOME="${ASTAH_HOME:-C:/Program Files/astah-UML}"
JAVA="$ASTAH_HOME/jre/bin/java.exe"
win() { cygpath -m "$1" 2>/dev/null || echo "$1"; }
LIB="$(win "$A1/build/lib")"
CP="$ASTAH_HOME/astah-uml.jar;$ASTAH_HOME/astah-api.jar;$LIB/nashorn-core-15.4.jar;$LIB/asm-7.3.1.jar;$LIB/asm-analysis-7.3.1.jar;$LIB/asm-commons-7.3.1.jar;$LIB/asm-tree-7.3.1.jar;$LIB/asm-util-7.3.1.jar"
mkdir -p "$A2/build" "$A2/diagrams"
rm -f "$A2/beets-a2-usecases.asta"
"$JAVA" -Xmx1g "-Djava.library.path=$ASTAH_HOME/lib/rlm" -cp "$CP" "$(win "$A1/astah/RunScripts.java")" \
    new "$(win "$A2/beets-a2-usecases.asta")" "$(win "$HERE")" "$(win "$A2/build")" "$(win "$HERE/usecases.js")" \
    2>&1 | grep -v 'cds\]' | grep -v '<INFO>'
rm -rf "$A2/build/img"
"$JAVA" -Xmx1g "-Djava.library.path=$ASTAH_HOME/lib/rlm" -cp "$ASTAH_HOME/astah-uml.jar" com.change_vision.jude.cmdline.JudeCommandRunner \
    -image all -f "$(cygpath -w "$A2/beets-a2-usecases.asta")" -t png -o "$(cygpath -w "$A2/build/img")" > /dev/null 2>&1
find "$A2/build/img" -name '*.png' -exec cp {} "$A2/diagrams/" \;
ls "$A2/diagrams"
