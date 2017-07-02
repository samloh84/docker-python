FROM samloh84/centos:7

ARG PRODUCT=python2
ARG PRODUCT_VERSION=2.7.13
ARG TEMP_DIR_ROOT=/tmp/${PRODUCT}
ARG TEMP_DIR=/${TEMP_DIR_ROOT}/${PRODUCT_VERSION}
ARG INSTALL_DIR_ROOT=/opt/${PRODUCT}
ARG INSTALL_DIR=${INSTALL_DIR_ROOT}/${PRODUCT_VERSION}

ARG PYTHON2_SRC_TARXZ_URL="https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tar.xz"
ARG PYTHON2_SRC_TARXZ=Python-2.7.13.tar.xz
ARG PYTHON2_SRC_TARXZ_MD5SUM=53b43534153bb2a0363f08bae8b9d990

ARG PYTHON2_KEYS_URL="https://www.python.org/static/files/pubkeys.txt"
ARG PYTHON2_SRC_TARXZ_ASC_URL="https://www.python.org/ftp/python/2.7.13/Python-2.7.13.tar.xz.asc"
ARG PYTHON2_SRC_TARXZ_ASC=Python-2.7.13.tar.xz.asc

USER ${ROOT_UID}

RUN \
PYTHON2_COMPILE_DEPENDENCIES="gcc gcc-c++ make zlib-devel openssl-devel readline-devel bzip2-devel gdbm-devel tk-devel sqlite-devel" && \
yum-install ${PYTHON2_COMPILE_DEPENDENCIES} && \
mkdir -p ${TEMP_DIR} ${INSTALL_DIR} && \
pushd ${TEMP_DIR} && \
curl -LjSs \
${PYTHON2_SRC_TARXZ_URL} -o ${PYTHON2_SRC_TARXZ} && \
curl -LjSs \
${PYTHON2_SRC_TARXZ_ASC_URL} -o ${PYTHON2_SRC_TARXZ_ASC} && \
curl -LjSs \
${PYTHON2_KEYS_URL} -o KEYS && \
echo "${PYTHON2_SRC_TARXZ_MD5SUM}  ${PYTHON2_SRC_TARXZ}" | md5sum -c - && \
gpg --import ./KEYS && \
gpg --verify ${PYTHON2_SRC_TARXZ_ASC} ${PYTHON2_SRC_TARXZ} && \
tar -xf ${PYTHON2_SRC_TARXZ} --strip-components=1 -C ${TEMP_DIR} && \
./configure --enable-optimizations --prefix=${INSTALL_DIR} && \
make && \
make install && \
pushd ${INSTALL_DIR} && \
PATH=${PATH}:${INSTALL_DIR}/bin ${INSTALL_DIR}/bin/python2 -m ensurepip && \
popd && \
fix-ownership ${INSTALL_DIR} && \
fix-permissions ${INSTALL_DIR} && \
yum remove -y ${PYTHON2_COMPILE_DEPENDENCIES} && \
yum clean all && \
popd && \
rm -rf ${TEMP_DIR_ROOT}

ENV PYTHON2_HOME ${INSTALL_DIR}
ENV PATH ${PYTHON2_HOME}/bin:${PATH}

USER ${APP_UID}
