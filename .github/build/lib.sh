#!/bin/bash

GIT_OPENSSL="https://github.com/drwetter/openssl-pm-snapshot.git"
GIT_BINUTILS_GDB="https://github.com/bminor/binutils-gdb.git"
GIT_READLINE="https://git.savannah.gnu.org/git/readline.git"
GIT_NCURSES="https://github.com/ThomasDickey/ncurses-snapshots.git"
GIT_LIBPCAP="https://github.com/the-tcpdump-group/libpcap.git"

BUILD_DIRECTORY="/build"
OUTPUT_DIRECTORY="/output"
GCC_OPTS="-static -fPIC"
GXX_OPTS="-static -static-libstdc++ -fPIC"
TMP_DIR=$(mktemp -dt building_lib.XXXXXX)
trap "rm -rf ${TMP_DIR}" EXIT TERM

# 配置初始化环境
init_lib(){
    CURRENT_ARCH="$1"
    if [ ! -d "$BUILD_DIRECTORY" ];then
        mkdir -p $BUILD_DIRECTORY
    fi
    if [ ! -d "$OUTPUT_DIRECTORY" ];then
        mkdir -p $OUTPUT_DIRECTORY
    fi
}

# 设置 HTTP 代理
set_http_proxy(){
    proxy=$1
    export http_proxy="$proxy"
    export https_proxy="$proxy"
    git config --global http.proxy "$proxy"
}

get_host_triple(){
    local host
    if [ "$CURRENT_ARCH" == "x86" ];then
        host="i686-linux-musl"
    elif [ "$CURRENT_ARCH" == "x86_64" ];then
        host="x86_64-linux-musl"
    elif [ "$CURRENT_ARCH" == "armhf" ];then
        host="arm-linux-musleabihf"
    elif [ "$CURRENT_ARCH" == "aarch64" ];then
        host="aarch64-linux-musl"
    fi
    echo $host
}

# 获取源文件
fetch(){
    if [ "$#" -ne 3 ];then
        echo "fetch() requires a source, destination and method."
        echo "Example: fetch http://github.com/test.git /build/test git"
        exit 1
    fi

    source=$1
    shift
    destination=$1
    shift
    method=$@

    if [ -d "$destination" ] || [ -f "$destination" ];then
        echo "Destination ${destination} already exists, skipping."
        return
    fi
    if [ "${method,,}" == "http" ];then
        cd /tmp || { echo "Could not cd to /tmp"; exit 1; }
        headers=$(mktemp headers.XXXXXX)
        curl -L -D "$headers" -sOJ "$source"
        filename=$(cat "$headers" | grep -o -E 'filename=.*$' | sed -e 's/filename=//')
        filename=$(trim "$filename")
        extract "$filename" "$destination"
        trap "rm -rf ${headers} /tmp/'${filename}'" EXIT TERM
    elif [ "${method,,}" == "git" ];then
        git clone "$source" "$destination"
    else
        echo "Invalid method ${method}"
        exit 1
    fi
}

# 解压压缩包
extract(){
    if [ "$#" -ne 2 ];then
        echo "extract() requires a source and destination."
        exit 1
    fi

    source=$1
    destination=$2
    if [ ! -d "$destination" ];then
        mkdir -p "$destination"
    fi
    if [ -f "$source" ] ; then
      case $source in
        *.tar.bz2)   tar xjf "$source" -C "$destination" --strip-components 1  ;;  
        *.tar.gz)    tar xzf "$source" -C "$destination" --strip-components 1  ;;  
        *.tar.xz)    tar xvfJ "$source" -C "$destination" --strip-components 1 ;;  
        *.tar)       tar xf "$source" -C "$destination" --strip-components 1   ;;  
        *.tbz2)      tar xjf "$source" -C "$destination" --strip-components 1  ;;  
        *.tgz)       tar xzf "$source" -C "$destination" --strip-components 1  ;;  
        *)     echo "'${source}' cannot be extracted via extract()" ;;
      esac
    else
        echo "'${source}' is not a valid file"
    fi  
}

# 清理前后空字符
trim(){
    local var="$*"
    var="${var#"${var%%[![:space:]]*}"}"
    var="${var%"${var##*[![:space:]]}"}"   
    echo -n "$var"
}

# 确定版本
get_version(){
    local cmd="$1"
    if [ -z "$cmd" ];then
        echo "Please provide a command to determine the version" >&2
        echo "Example: /build/test --version | awk '{print \$2}'" >&2
        exit 1
    fi

    local version="-"
    if [ "$CURRENT_ARCH" == "armhf" ];then
        if which qemu-arm 1>&2 2>/dev/null;then
            cmd="qemu-arm ${cmd}"
            version+=$(eval "$cmd")
        else
            echo "qemu-arm not found, skipping ARMHF version checks." >&2
        fi
    elif [ "$CURRENT_ARCH" == "aarch64" ];then
        if which qemu-aarch64 1>&2 2>/dev/null;then
            cmd="qemu-aarch64 ${cmd}"
            version+=$(eval "$cmd")
        else
            echo "qemu-aarch64 not found, skipping AARCH64 version checks." >&2
        fi
    else
        version+=$(eval "$cmd")
    fi
    if [ "$version" == "-" ];then
        version+="${CURRENT_ARCH}"
    else
        version+="-${CURRENT_ARCH}"
    fi
    echo "$version"
}

lib_create_tmp_dir(){
    local tmp_dir=$(mktemp -dt -p ${TMP_DIR} tmpdir.XXXXXX)
    echo "$tmp_dir"
}

lib_check_lib_arch(){
    lib=$1
    if [ ! -f "$lib" ];then
        echo ""
        return
    fi

    local tmp_dir=$(lib_create_tmp_dir)
    cp "$lib" "$tmp_dir"
    bash -c "cd ${tmp_dir}; ar x $(basename ${lib})"
    local output=$(find "${tmp_dir}" -name "*.o" -exec file {} \;)
    if echo "$output" | grep -q "Intel 80386";then
        echo "Arch of ${lib} is x86" >&2
        echo "x86"
    elif echo "$output" | grep -q "x86-64";then
        echo "Arch of ${lib} is x86_64" >&2
        echo "x86_64"
    elif echo "$output" | grep -q "ARM aarch64";then
        echo "Arch of ${lib} is armhf" >&2
        echo "armhf"
    elif echo "$output" | grep -q "ARM,";then
        echo "Arch of ${lib} is aarch64" >&2
        echo "aarch64"
    else
        echo "Could not determine arch of library ${lib}" >&2
        echo ""
    fi
}

lib_build_openssl(){
    local version=$1
    fetch "$GIT_OPENSSL" "${BUILD_DIRECTORY}/openssl" git
    cd "${BUILD_DIRECTORY}/openssl" || { echo "Cannot cd to ${BUILD_DIRECTORY}/openssl"; exit 1; }
    if [ -n "$version" ];then
        git checkout "$version" || echo "Version ${version} not found, continuing with master."
    fi
    if [ -f "${BUILD_DIRECTORY}/openssl/libssl.a" ];then
        lib_arch=$(lib_check_lib_arch "${BUILD_DIRECTORY}/openssl/libssl.a")
        if [ "$lib_arch" != "$CURRENT_ARCH" ];then
            echo "Rebuild for current arch"
            git clean -fdx || true
        else
            echo "[+] OpenSSL already available for current arch, skipping building"
            return
        fi
    fi
    local openssl_arch
    if [ "${CURRENT_ARCH}" == "x86" ] ||
        [ "${CURRENT_ARCH}" == "armhf" ];then
        openssl_arch="linux-generic32"
    elif [ "${CURRENT_ARCH}" == "x86_64" ];then
        openssl_arch="linux-x86_64"
    elif [ "${CURRENT_ARCH}" == "aarch64" ];then
        openssl_arch="linux-generic64"
    fi
    CFLAGS="${GCC_OPTS}" \
        ./Configure \
            no-shared \
            "$openssl_arch"
    make -j4
    echo "[+] Finished building OpenSSL ${CURRENT_ARCH}"
}

lib_build_zlib(){
    fetch "$GIT_BINUTILS_GDB" "${BUILD_DIRECTORY}/binutils-gdb" git
    cd "${BUILD_DIRECTORY}/binutils-gdb/zlib" || { echo "Cannot cd to ${BUILD_DIRECTORY}/binutils-gdb/zlib"; exit 1; }
    git clean -fdx
    CC="gcc ${GCC_OPTS}" \
        CXX="g++ ${GXX_OPTS}" \
        /bin/bash ./configure \
            --host="$(get_host_triple)" \
            --enable-static
    make -j4
    echo "[+] Finished building zlib ${CURRENT_ARCH}"
}

lib_build_readline(){
    fetch "$GIT_READLINE" "${BUILD_DIRECTORY}/readline" git
    cd "${BUILD_DIRECTORY}/readline" || { echo "Cannot cd to ${BUILD_DIRECTORY}/readline"; exit 1; }
    git clean -fdx
    CFLAGS="${GCC_OPTS}" \
        CXXFLAGS="${GXX_OPTS}" \
        ./configure \
            --host="$(get_host_triple)" \
            --disable-shared \
            --enable-static
    make -j4
    echo "[+] Finished building readline ${CURRENT_ARCH}"
}

lib_build_ncurses(){
    fetch "$GIT_NCURSES" "${BUILD_DIRECTORY}/ncurses" git
    cd "${BUILD_DIRECTORY}/ncurses" || { echo "Cannot cd to ${BUILD_DIRECTORY}/ncurses"; exit 1; }
    git clean -fdx
    git checkout v6_2

    CMD="CFLAGS=\"${GCC_OPTS}\" "
    CMD+="CXXFLAGS=\"${GXX_OPTS}\" "
    CMD+="./configure --host=$(get_host_triple) --disable-shared --enable-static"
    if [ "$CURRENT_ARCH"!="x86" -a "$CURRENT_ARCH"!="x86_64" ];then
        CMD+=" --with-build-cc=/x86_64-linux-musl-cross/bin/x86_64-linux-musl-gcc"
    fi
    eval "$CMD"
    make -j4
    echo "[+] Finished building ncurses ${CURRENT_ARCH}"
}

lib_build_libpcap(){
    fetch "$GIT_LIBPCAP" "${BUILD_DIRECTORY}/libpcap" git
    cd "${BUILD_DIRECTORY}/libpcap" || { echo "Cannot cd to ${BUILD_DIRECTORY}/libpcap"; exit 1; }
    git clean -fdx
    git checkout libpcap-1.9.1
    CFLAGS="${GCC_OPTS}" \
        CXXFLAGS="${GXX_OPTS}" \
        ./configure \
            --host="$(get_host_triple)" \
            --with-pcap=linux \
            --disable-shared \
            --enable-static
    make -j4
    echo "[+] Finished building libpcap ${CURRENT_ARCH}"
}
