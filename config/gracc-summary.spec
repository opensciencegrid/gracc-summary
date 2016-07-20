Name:           gracc-summary
Version:        1.0
Release:        1%{?dist}
Summary:        GRACC Summary Agents

License:        ASL 2.0
URL:            https://opensciencegrid.github.io/gracc/
Source0:        gracc-summary-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python-setuptools
BuildRequires:  systemd
BuildRequires:  python-srpm-macros 
BuildRequires:  python-rpm-macros 
BuildRequires:  python2-rpm-macros 
BuildRequires:  epel-rpm-macros
BuildRequires:  systemd
Requires:       python2-pika
Requires:       python-toml
Requires(pre):  shadow-utils

%description
GRACC Summary Agents


%pre
getent group gracc >/dev/null || groupadd -r gracc
getent passwd gracc >/dev/null || \
    useradd -r -g gracc -d /tmp -s /sbin/nologin \
    -c "GRACC Services Account" gracc
exit 0

%prep
%setup -q


%build
%{py2_build}


%install
%{py2_install}


install -d -m 0755 $RPM_BUILD_ROOT/%{_sysconfdir}/graccsum/config.d/
install -m 0744 config/gracc-summary.toml $RPM_BUILD_ROOT/%{_sysconfdir}/graccreq/config.d/gracc-summary.toml
install -d -m 0755 $RPM_BUILD_ROOT/%{_unitdir}
install -m 0744 config/graccsum.service $RPM_BUILD_ROOT/%{_unitdir}/
install -m 0744 config/graccsumperiodic.service $RPM_BUILD_ROOT/%{_unitdir}/



%files
%defattr(-, gracc, gracc)
%{python2_sitelib}/graccsum
%{python2_sitelib}/graccsum-%{version}-py2.?.egg-info
%attr(755, root, root) %{_bindir}/*
%{_unitdir}/graccsum.service
%{_unitdir}/graccsumperiodic.service
%config %{_sysconfdir}/graccsum/config.d/gracc-summary.toml

%doc



%changelog

* Wed Jul 20 2016 Derek Weitzel <dweitzel@cse.unl.edu> 1.1-1
- Initial build

