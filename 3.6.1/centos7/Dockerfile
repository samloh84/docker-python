FROM samloh84/centos:7

ARG PRODUCT=python3
ARG PRODUCT_VERSION=3.6.1
ARG TEMP_DIR_ROOT=/tmp/${PRODUCT}
ARG TEMP_DIR=/${TEMP_DIR_ROOT}/${PRODUCT_VERSION}
ARG INSTALL_DIR_ROOT=/opt/${PRODUCT}
ARG INSTALL_DIR=${INSTALL_DIR_ROOT}/${PRODUCT_VERSION}

ARG PYTHON3_SRC_TARXZ_URL="https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz"
ARG PYTHON3_SRC_TARXZ=Python-3.6.1.tar.xz
ARG PYTHON3_SRC_TARXZ_MD5SUM=692b4fc3a2ba0d54d1495d4ead5b0b5c

ARG PYTHON3_KEYS_URL="https://www.python.org/static/files/pubkeys.txt"
ARG PYTHON3_SRC_TARXZ_ASC_URL="https://www.python.org/ftp/python/3.6.1/Python-3.6.1.tar.xz.asc"
ARG PYTHON3_SRC_TARXZ_ASC=Python-3.6.1.tar.xz.asc

USER ${ROOT_UID}

RUN \
PYTHON3_COMPILE_DEPENDENCIES="gcc gcc-c++ make zlib-devel openssl-devel readline-devel bzip2-devel xz-devel gdbm-devel tk-devel sqlite-devel" && \
yum-install ${PYTHON3_COMPILE_DEPENDENCIES} && \
mkdir -p ${TEMP_DIR} ${INSTALL_DIR} && \
pushd ${TEMP_DIR} && \
curl -LjSs \
${PYTHON3_SRC_TARXZ_URL} -o ${PYTHON3_SRC_TARXZ} && \
curl -LjSs \
${PYTHON3_SRC_TARXZ_ASC_URL} -o ${PYTHON3_SRC_TARXZ_ASC} && \
curl -LjSs \
${PYTHON3_KEYS_URL} -o KEYS && \
echo "${PYTHON3_SRC_TARXZ_MD5SUM}  ${PYTHON3_SRC_TARXZ}" | md5sum -c - && \
gpg --import ./KEYS && \
gpg --verify ${PYTHON3_SRC_TARXZ_ASC} ${PYTHON3_SRC_TARXZ} && \
tar -xf ${PYTHON3_SRC_TARXZ} --strip-components=1 -C ${TEMP_DIR} && \
./configure --enable-optimizations --prefix=${INSTALL_DIR} && \
make && \
make install && \
pushd ${INSTALL_DIR} && \
PATH=${PATH}:${INSTALL_DIR}/bin ${INSTALL_DIR}/bin/pip install -U pip && \
popd && \
fix-ownership ${INSTALL_DIR} && \
fix-permissions ${INSTALL_DIR} && \
yum remove -y ${PYTHON3_COMPILE_DEPENDENCIES} && \
yum clean all && \
popd && \
rm -rf ${TEMP_DIR_ROOT}

ENV PYTHON3_HOME ${INSTALL_DIR}
ENV PATH ${PYTHON3_HOME}/bin:${PATH}

USER ${APP_UID}
