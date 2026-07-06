#!/bin/bash
# Build only the changed classes and update the existing JAR
set -e

SFS2X_DIR="/workspaces/MSM/msm-server/sfs2x/SFS2X"
SRC_DIR="/workspaces/MSM/msmsandbox-master/MSMSandbox/src"
BUILD_DIR="/workspaces/MSM/msm-server/build/classes"
EXTENSION_DIR="$SFS2X_DIR/extensions/MSMSandbox"
ORIGINAL_JAR="$EXTENSION_DIR/mainExtension.jar"

# Need SFS2X jars for classes that depend on them
SFS2X_CP="$SFS2X_DIR/lib/sfs2x-core.jar:$SFS2X_DIR/lib/sfs2x.jar:$SFS2X_DIR/lib/sfs2x-lib.jar:$SFS2X_DIR/lib/sfs2x-util.jar"
EXT_CP="$SFS2X_DIR/extensions/__lib__/gson-2.10.1.jar:$SFS2X_DIR/extensions/__lib__/json-20231013.jar:$SFS2X_DIR/extensions/__lib__/sqlite-jdbc-3.49.1.0.jar"
CLASSPATH="$SFS2X_CP:$EXT_CP"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

JAVA_FLAGS="--release 11"

echo "=== Step 1: Compile SQLHandler.java (no SFS2X deps) ==="
javac $JAVA_FLAGS -cp "$EXT_CP" -d "$BUILD_DIR" "$SRC_DIR/server/Tools/SQLHandler.java"

echo "=== Step 2: Compile MSMClient.java (needs SFS2X client API + existing classes) ==="
SFS2X_CP_EXTRA="$SFS2X_DIR/extensions/__lib__/sfs2x-client-core.jar:$SFS2X_DIR/extensions/__lib__/SFS2X_API_Java.jar:$SFS2X_DIR/extensions/__lib__/netty-3.2.2.Final.jar"
javac $JAVA_FLAGS -cp "$CLASSPATH:$BUILD_DIR:$ORIGINAL_JAR:$SFS2X_CP_EXTRA" \
  -d "$BUILD_DIR" \
  "$SRC_DIR/server/Tools/MSMClient.java"

echo "=== Step 3: Compile PlayerIslandFactory.java (needs SFS2X + existing classes) ==="
javac $JAVA_FLAGS -cp "$CLASSPATH:$BUILD_DIR:$ORIGINAL_JAR" \
  -d "$BUILD_DIR" \
  "$SRC_DIR/server/Entities/PlayerIslandFactory.java"

echo "=== Step 4: Update JAR ==="
cp "$ORIGINAL_JAR" "${ORIGINAL_JAR}.bak"
cd "$BUILD_DIR"
jar uf "$ORIGINAL_JAR" \
  server/Tools/SQLHandler.class \
  server/Tools/MSMClient.class \
  'server/Tools/MSMClient$FileMapping.class' \
  server/Entities/PlayerIslandFactory.class

echo "=== Done ==="
echo "Backup: ${ORIGINAL_JAR}.bak"
echo "Updated: $ORIGINAL_JAR"
jar tf "$ORIGINAL_JAR" | grep -E "SQLHandler|PlayerIslandFactory"
