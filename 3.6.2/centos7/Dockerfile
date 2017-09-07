FROM samloh84/centos:7
ARG PRODUCT=python3
ARG PRODUCT_VERSION=3.6.2
ARG TEMP_DIR_ROOT=/tmp/${PRODUCT}
ARG TEMP_DIR=/${TEMP_DIR_ROOT}/${PRODUCT_VERSION}
ARG INSTALL_DIR_ROOT=/opt/${PRODUCT}
ARG INSTALL_DIR=${INSTALL_DIR_ROOT}/${PRODUCT_VERSION}

ARG PYTHON_SOURCE_URL="https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz"
ARG PYTHON_SOURCE="Python-3.6.2.tar.xz"
ARG PYTHON_GPG_KEYS_URL=https://www.python.org/static/files/pubkeys.txt
ARG PYTHON_GPG_KEYS=pubkeys.txt
ARG PYTHON_SIGNATURE_URL="https://www.python.org/ftp/python/3.6.2/Python-3.6.2.tar.xz.asc"
ARG PYTHON_SIGNATURE="Python-3.6.2.tar.xz.asc"

USER ${ROOT_UID}

RUN \
mkdir -p ${TEMP_DIR} ${INSTALL_DIR} && \
cd ${TEMP_DIR} && \
curl -LjSs ${PYTHON_SOURCE_URL} -o ${PYTHON_SOURCE} && \
curl -LjSs ${PYTHON_GPG_KEYS_URL} -o ${PYTHON_GPG_KEYS} && \
curl -LjSs ${PYTHON_SIGNATURE_URL} -o ${PYTHON_SIGNATURE} && \
gpg --import ${PYTHON_GPG_KEYS} && \
curl -LjSs ${PYTHON_SIGNATURE_URL} -o ${PYTHON_SIGNATURE} && \
gpg --verify ${PYTHON_SIGNATURE} && \
PYTHON3_COMPILE_DEPENDENCIES="gcc gcc-c++ make zlib-devel openssl-devel readline-devel bzip2-devel xz-devel gdbm-devel tk-devel sqlite-devel" && \
yum-install ${PYTHON3_COMPILE_DEPENDENCIES} && \
mkdir -p ${TEMP_DIR}/build && \
tar -xf ${PYTHON_SOURCE} --strip-components=1 -C ${TEMP_DIR}/build && \
cd ${TEMP_DIR}/build && \
./configure --enable-optimizations --prefix=${INSTALL_DIR} && \
make && \
make install && \
cd ${INSTALL_DIR} && \
PATH=${PATH}:${INSTALL_DIR}/bin ${INSTALL_DIR}/bin/pip3 install -U pip && \
yum remove -y ${PYTHON3_COMPILE_DEPENDENCIES} && \
yum clean all && \
fix-ownership ${INSTALL_DIR} && \
fix-permissions ${INSTALL_DIR} && \
rm -rf ${TEMP_DIR_ROOT}

ENV PYTHON3_HOME ${INSTALL_DIR}
ENV PATH ${PYTHON3_HOME}/bin:${PATH}

USER ${APP_UID}