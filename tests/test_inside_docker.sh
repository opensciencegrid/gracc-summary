#!/bin/sh -xe


# Install all the things
rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
curl -o /etc/yum.repos.d/djw8605-GRACC-epel-7.repo https://copr.fedorainfracloud.org/coprs/djw8605/GRACC/repo/epel-7/djw8605-GRACC-epel-7.repo 
yum -y update

yum -y install python-pip git rabbitmq-server java-1.8.0-openjdk python-elasticsearch-dsl rpm-build python-srpm-macros python-rpm-macros gracc-request python2-rpm-macros epel-rpm-macros which
rpm -Uvh https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.1.1.rpm
rpm -Uvh https://download.elastic.co/logstash/logstash/packages/centos/logstash-2.3.4-1.noarch.rpm

systemctl start elasticsearch.service


mkdir -p /usr/share/gracc/

# Create the rabbitmq exchange we need for summary records
systemctl start rabbitmq-server.service
sleep 2
python gracc-summary/tests/create_summary_exchange.py
cp gracc-summary/tests/logstash/gracc-summary-template.json /usr/share/gracc/gracc-summary-template.json
cp gracc-summary/tests/logstash/logstash.conf gracc-summary/tests/logstash/gracc-transfer-summary.conf /etc/logstash/conf.d
systemctl start logstash.service

cp gracc-summary/tests/graccreq/gracc-request.toml /etc/graccreq/config.d/gracc-request.toml
systemctl start graccreq.service
sleep 10
journalctl -u graccreq.service -n 100 --no-pager

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
cp -f gracc-summary/tests/gracc-summary-test.toml /etc/graccsum/config.d/gracc-summary.toml

#systemctl start graccsum.service

# Wait for the summarizer to start up
#sleep 10
#journalctl -u graccsum.service --no-pager


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
systemctl start graccsumperiodic.timer
systemctl status graccsumperiodic.timer
journalctl -u graccsumperiodic.timer -n 100 --no-pager
journalctl -u graccsumperiodic.service -n 100 --no-pager
# systemctl list-timers --all
sleep 65
journalctl -u graccsumperiodic.service --no-pager



pushd gracc-summary/
set +e
python -m unittest discover -v tests/unittests "test_*.py"
unittest_exit=$?
set -e
popd

sleep 2
journalctl -u graccreq.service --no-pager -n 100

journalctl -u logstash.service --no-pager -n 100
cat /var/log/logstash/*

journalctl -u graccsumperiodic.service --no-pager

# Look at the summarization profile metrics
cat /tmp/profile.txt

exit $unittest_exit

