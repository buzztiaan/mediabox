#! /bin/bash

CWD=`dirname $0`

function get_target {

  grep "Diablo" /etc/maemo_version >/dev/null
  if [ $? -eq 0 ]; then
    echo "maemo4"
  fi
  grep "Fremantle" /etc/maemo_version >/dev/null
  if [ $? -eq 0 ]; then
    echo "maemo5"
  fi

}


# determine name of build target
TARGET=`get_target`
echo "Building for target: ${TARGET}"

DEBDIR=${CWD}/debian
PKGNAME=`head -1 ${DEBDIR}/changelog | cut -d" " -f1`
TEMPDIR=/tmp/make-deb/${PKGNAME}

# copy all files to a temporary place
#ALL_FILES=`find ${CWD} | egrep -v ".svn|.xcf|~$|.pyo$|.pyc$|make\-deb.sh"`
rm -rf ${TEMPDIR}
echo "Copying:"
rsync -va \
      --exclude=".svn" \
      --exclude="*.xcf" \
      --exclude="*~" \
      --exclude="*.pyo" \
      --exclude="*.pyc" \
      --exclude="make-deb.sh" \
      ${CWD}/ ${TEMPDIR}/

#for FILE in ${ALL_FILES}; do
#  FPATH=${CWD}/${FILE}
#  if [ -f ${FPATH} ]; then
#    echo "  ${FILE}"
#    FDIR=`dirname ${FILE}`
#    mkdir -p ${TEMPDIR}/${FDIR}
#    cp -p ${FPATH} ${TEMPDIR}/${FDIR}/
#  fi
#done
echo ""

# run tidy script, if available
echo -n "Do we have 'make-tidy.sh'?     "
if [ -x ${TEMPDIR}/make-tidy.sh ]; then
  echo "YES. executing"
  ${TEMPDIR}/make-tidy.sh
  rm ${TEMPDIR}/make-tidy.sh
else
  echo "NO. skipping"
fi

# overlay target-specific debian stuff
mkdir -p ${TEMPDIR}/debian
cp ${DEBDIR}/** ${TEMPDIR}/debian/
TARGETFILES=`ls ${TEMPDIR}/debian/*`
for TF in ${TARGETFILES}; do
  if [ -e ${TF}.${TARGET} ]; then
    mv ${TF}.${TARGET} ${TF}
    echo "Overlaying ${TF}.${TARGET}"
  fi
done
echo ""

echo "Building package:"
echo ""
cd ${TEMPDIR}
dpkg-buildpackage -rfakeroot $*

