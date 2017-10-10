FROM samloh84/centos:7
ARG PRODUCT=python2
ARG PRODUCT_VERSION=2.7.14
ARG TEMP_DIR_ROOT=/tmp/${PRODUCT}
ARG TEMP_DIR=/${TEMP_DIR_ROOT}/${PRODUCT_VERSION}
ARG INSTALL_DIR_ROOT=/opt/${PRODUCT}
ARG INSTALL_DIR=${INSTALL_DIR_ROOT}/${PRODUCT_VERSION}

ARG PYTHON_SOURCE_URL="https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz"
ARG PYTHON_SOURCE="Python-2.7.14.tar.xz"
ARG PYTHON_GPG_KEYS_URL=https://www.python.org/static/files/pubkeys.txt
ARG PYTHON_GPG_KEYS=pubkeys.txt
ARG PYTHON_SIGNATURE_URL="https://www.python.org/ftp/python/2.7.14/Python-2.7.14.tar.xz.asc"
ARG PYTHON_SIGNATURE="Python-2.7.14.tar.xz.asc"

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
PYTHON2_COMPILE_DEPENDENCIES="gcc gcc-c++ make zlib-devel openssl-devel readline-devel bzip2-devel xz-devel gdbm-devel tk-devel sqlite-devel" && \
yum-install ${PYTHON2_COMPILE_DEPENDENCIES} && \
mkdir -p ${TEMP_DIR}/build && \
tar -xf ${PYTHON_SOURCE} --strip-components=1 -C ${TEMP_DIR}/build && \
cd ${TEMP_DIR}/build && \
./configure --enable-optimizations --prefix=${INSTALL_DIR} && \
make && \
make install && \
cd ${INSTALL_DIR} && \
PATH=${PATH}:${INSTALL_DIR}/bin ${INSTALL_DIR}/bin/python2 -m ensurepip && \
yum remove -y ${PYTHON2_COMPILE_DEPENDENCIES} && \
yum clean all && \
fix-ownership ${INSTALL_DIR} && \
fix-permissions ${INSTALL_DIR} && \
rm -rf ${TEMP_DIR_ROOT}

ENV PYTHON2_HOME ${INSTALL_DIR}
ENV PATH ${PYTHON2_HOME}/bin:${PATH}

USER ${APP_UID}