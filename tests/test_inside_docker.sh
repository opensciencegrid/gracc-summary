#!/bin/sh -xe


# Install all the things
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
curl -o /etc/yum.repos.d/djw8605-GRACC-epel-7.repo https://copr.fedorainfracloud.org/coprs/djw8605/GRACC/repo/epel-7/djw8605-GRACC-epel-7.repo 
yum -y update

yum -y install python-pip git rabbitmq-server java-1.8.0-openjdk python-elasticsearch-dsl rpm-build python-srpm-macros python-rpm-macros gracc-request python2-rpm-macros epel-rpm-macros
rpm -Uvh https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/rpm/elasticsearch/2.3.2/elasticsearch-2.3.2.rpm

systemctl start elasticsearch.service
systemctl start rabbitmq-server.service
systemctl start graccreq.service

# Prepare the RPM environment
mkdir -p /tmp/rpmbuild/{BUILD,RPMS,SOURCES,SPECS,SRPMS}
cat >> /etc/rpm/macros.dist << EOF
%dist .osg.el${OS_VERSION}
%osg 1
EOF

cp gracc-summary/config/gracc-summary.spec /tmp/rpmbuild/SPECS
package_version=`grep Version gracc-summary/config/gracc-summary.spec | awk '{print $2}'`
pushd gracc-summary
git archive --format=tar --prefix=gracc-summary-${package_version}/ HEAD  | gzip >/tmp/rpmbuild/SOURCES/gracc-summary-${package_version}.tar.gz
popd

# Build the RPM
rpmbuild --define '_topdir /tmp/rpmbuild' -ba /tmp/rpmbuild/SPECS/gracc-summary.spec

yum localinstall -y /tmp/rpmbuild/RPMS/noarch/gracc-summary*

# Copy in the test configuration
cp -f gracc-summary/tests/gracc-summary-test.toml /etc/graccreq/config.d/gracc-summary.toml

systemctl start graccsum.service

# Wait for the summarizer to start up
sleep 10
journalctl -u graccsum.service --no-pager


# Install the test data
curl -O https://nodejs.org/dist/v4.4.4/node-v4.4.4-linux-x64.tar.xz
tar xf node-v4.4.4-linux-x64.tar.xz
export PATH=$PATH:`pwd`/node-v4.4.4-linux-x64/bin
npm install elasticdump -g

git clone https://github.com/djw8605/gracc-test-data.git
pushd gracc-test-data
bash -x ./import.sh
popd

# Start the gracc periodic summarizer after data has been imported
systemctl start graccsumperiodic.service
sleep 10
journalctl -u graccsumperiodic.service --no-pager

pushd gracc-summary
python -m unittest discover tests/unittests "test_*.py"
popd

sleep 30
journalctl -u graccsum.service --no-pager -n 20



