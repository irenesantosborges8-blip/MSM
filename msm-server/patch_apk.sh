#!/bin/bash
# MSM APK Patcher - Modifica o APK para conectar ao servidor local
set -e

APK_WORK="/workspaces/MSM/apk-work"
APK_FILE="$1"
KEYSTORE="$APK_WORK/msm.keystore"
STOREPASS="msm123"
ALIAS="msm"
AUTH_HOST="${AUTH_HOST:-127.0.0.1}"
AUTH_PORT="${AUTH_PORT:-8082}"

if [ -z "$APK_FILE" ]; then
    echo "Uso: $0 <arquivo.apk>"
    echo "Ex:  $0 msm-4.8.4.apk"
    ls "$APK_WORK"/*.apk 2>/dev/null || echo "(nenhum APK encontrado em $APK_WORK)"
    exit 1
fi

APK_PATH="$APK_WORK/$APK_FILE"
if [ ! -f "$APK_PATH" ]; then
    echo "Arquivo não encontrado: $APK_PATH"
    exit 1
fi

echo "=== MSM APK Patcher ==="
echo "APK: $APK_PATH"
echo "Auth: http://$AUTH_HOST:$AUTH_PORT"
echo ""

# Limpar diretório de trabalho
WORKDIR="$APK_WORK/extract"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"

# Extrair APK
echo "[1/5] Extraindo APK..."
unzip -q "$APK_PATH" -d "$WORKDIR"
echo "  Extraído."

# Encontrar app.properties
PROPS=$(find "$WORKDIR" -name "app.properties" -type f 2>/dev/null)
# Remover assinatura antiga
rm -rf "$WORKDIR/META-INF"

if [ -z "$PROPS" ]; then
    echo "[!] app.properties não encontrado!"
    echo "  Procurando arquivos com URLs de servidor..."
    URL_FILES=$(grep -rl "bbbgame\|auth\.bbb\|pregame_setup\|auth/api" "$WORKDIR" 2>/dev/null | head -10)
    if [ -n "$URL_FILES" ]; then
        echo "  URLs encontradas em:"
        echo "$URL_FILES"
        for f in $URL_FILES; do
            cp "$f" "$f.bak"
            sed -i "s|https://auth\.bbbgame\.net/auth/api/token[^[:space:]]*|http://$AUTH_HOST:$AUTH_PORT/auth/api/token/|g" "$f"
            sed -i "s|https://auth\.bbbgame\.net/pregame_setup[^[:space:]]*|http://$AUTH_HOST:$AUTH_PORT/pregame_setup|g" "$f"
            sed -i "s|https://auth\.bbbgame\.net|http://$AUTH_HOST:$AUTH_PORT|g" "$f"
            echo "  Patchado: $f"
        done
    else
        echo "  Nenhuma URL conhecida encontrada."
        echo ""
        echo "  Estrutura do APK:"
        find "$WORKDIR" -type f | head -50
        exit 1
    fi
else
    echo "[2/5] app.properties encontrado: $PROPS"
    echo "  Conteúdo original:"
    grep -i "auth\|url\|server\|bbb" "$PROPS" 2>/dev/null || echo "  (nenhuma URL encontrada)"

    cp "$PROPS" "$PROPS.bak"

    echo "[3/5] Aplicando patch..."
    # Patching BBB_AUTH_SERVER (pregame setup) - matches bbbgame.net or msm-auth.bbbgame.net
    if grep -q "BBB_AUTH_SERVER=" "$PROPS" 2>/dev/null; then
        sed -i "s|BBB_AUTH_SERVER=.*|BBB_AUTH_SERVER=http://$AUTH_HOST:$AUTH_PORT/pregame_setup|g" "$PROPS"
        echo "  Patch BBB_AUTH_SERVER -> /pregame_setup"
    fi
    # Patching BBB_AUTH1_SERVER (pregame setup, alternative name)
    if grep -q "BBB_AUTH1_SERVER=" "$PROPS" 2>/dev/null; then
        sed -i "s|BBB_AUTH1_SERVER=.*|BBB_AUTH1_SERVER=http://$AUTH_HOST:$AUTH_PORT/pregame_setup|g" "$PROPS"
        echo "  Patch BBB_AUTH1_SERVER -> /pregame_setup"
    fi
    # Patching BBB_AUTH2_SERVER (token endpoint)
    if grep -q "BBB_AUTH2_SERVER=" "$PROPS" 2>/dev/null; then
        sed -i "s|BBB_AUTH2_SERVER=.*|BBB_AUTH2_SERVER=http://$AUTH_HOST:$AUTH_PORT/auth/api/token/|g" "$PROPS"
        echo "  Patch BBB_AUTH2_SERVER -> /auth/api/token/"
    fi
    # Fallback: replace any bbbgame.net URLs
    if grep -q "bbbgame.net" "$PROPS" 2>/dev/null; then
        sed -i "s|https://[^/]*bbbgame\.net[^[:space:]]*|http://$AUTH_HOST:$AUTH_PORT|g" "$PROPS"
        echo "  Patch fallback: removed bbbgame.net URLs"
    fi

    echo "  Conteúdo final:"
    grep -i "auth\|url\|server" "$PROPS" 2>/dev/null || echo "  (vazio)"
fi

# Repack APK
echo "[4/5] Reempacotando APK..."
cd "$WORKDIR"
rm -f "$APK_WORK/msm-patched-unsigned.apk"
zip -r -q "$APK_WORK/msm-patched-unsigned.apk" .
echo "  Reempacotado."

# Alinhar (se zipalign disponível)
if which zipalign &>/dev/null; then
    echo "  Alinhando com zipalign..."
    zipalign -f 4 "$APK_WORK/msm-patched-unsigned.apk" "$APK_WORK/msm-patched-aligned.apk"
    mv "$APK_WORK/msm-patched-aligned.apk" "$APK_WORK/msm-patched-unsigned.apk"
fi

# Assinar
echo "[5/5] Assinando APK..."
jarsigner -keystore "$KEYSTORE" -storepass "$STOREPASS" -keypass "$STOREPASS" \
    -sigalg SHA256withRSA -digestalg SHA-256 \
    "$APK_WORK/msm-patched-unsigned.apk" "$ALIAS" 2>&1 | grep -v "Warning:"

# Verificar
jarsigner -verify -keystore "$KEYSTORE" "$APK_WORK/msm-patched-unsigned.apk" 2>&1 | grep -E "jar verified|signatures"

# Renomear
cp "$APK_WORK/msm-patched-unsigned.apk" "$APK_WORK/msm-patched.apk"
echo ""
echo "=== APK patchado com sucesso! ==="
echo "Arquivo: $APK_WORK/msm-patched.apk"
ls -lh "$APK_WORK/msm-patched.apk"
echo ""
echo "Instale no seu dispositivo Android e conecte ao servidor em $AUTH_HOST:$AUTH_PORT"
