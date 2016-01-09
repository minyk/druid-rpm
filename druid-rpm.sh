#!/bin/sh
NAME='Druid'

PKGNAME='druid'

VERSION=${1:-"0.8.2"}
GITHUB_RELEASE=${2:-"druid-0.8.2"}

RELEASE=${3:-"1"}

set -ex

rm -rf BUILD BUILDROOT SOURCES RPMS SRPMS tmp || true
mkdir -p BUILD RPMS SRPMS SOURCES

cp -r $PKGNAME/* SOURCES/
cp bigtop.bom SOURCES/bigtop.bom

if [ ! -f SOURCES/$PKGNAME-$VERSION-src.tar.gz ];
then
    curl --retry 5 -# -L -k -o SOURCES/$PKGNAME-$VERSION-src.tar.gz https://github.com/druid-io/druid/archive/$GITHUB_RELEASE.tar.gz
fi

rpmbuild -ba --define="_topdir $PWD" --define="_tmppath $PWD/tmp" \
 --define="druid_server_version $VERSION" \
 --define="druid_server_release $RELEASE" \
 $PKGNAME.spec
