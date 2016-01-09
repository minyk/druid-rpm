# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
%define etc_druid_server_conf %{_sysconfdir}/%{name}/conf
%define etc_druid_server_conf_dist %{etc_druid_server_conf}.dist
%define druid_server_home /usr/lib/%{name}
%define man_dir %{_mandir}
%define druid_services broker coordinator historical middlemanager overlord router realtime

%if %{!?suse_version:1}0 && %{!?mgaversion:1}0

%define __os_install_post \
    /usr/lib/rpm/redhat/brp-compress ; \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} ; \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} ; \
    /usr/lib/rpm/brp-python-bytecompile ; \
    %{nil}

%define alternatives_cmd alternatives
%global initd_dir %{_sysconfdir}/rc.d/init.d
%endif


%if  %{?suse_version:1}0

# Only tested on openSUSE 11.4. le'ts update it for previous release when confirmed
%if 0%{suse_version} > 1130
%define suse_check \# Define an empty suse_check for compatibility with older sles
%endif

%define alternatives_cmd update-alternatives
%global initd_dir %{_sysconfdir}/rc.d
%define __os_install_post \
    %{suse_check} ; \
    /usr/lib/rpm/brp-compress ; \
    %{nil}

%endif

%define __jar_repack 0
%define _unpackaged_files_terminate_build 0
%define _missing_doc_files_terminate_build 0

Name: druid	
Version: %{druid_server_version}
Release: %{druid_server_release}
Summary: Druid	
Group: Applications/Internet
License: Apache License 2.0
URL: http://http://druid.io/
Source: druid-%{version}-src.tar.gz
SOURCE1: do-component-build
SOURCE2: install_%{name}.sh
SOURCE4: init.d.tmpl
BuildRoot: %{_tmppath}/%{name}-root
BuildArch: noarch
Requires: bigtop-utils
Requires: /lib/lsb/init-functions

%description
An open-source, real-time data store designed to power interactive applications at scale.

%package examples
Summary: Druid Examples
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description examples
Example data for Druid

%package broker
Summary: Druid Broker Server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description broker
Druid Broker Server

%package historical
Summary: Druid Historical Server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description historical
Druid Historical Server

%package realtime
Summary: Druid Realtime Server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description realtime
Druid Realtime Server

%package coordinator
Summary: Druid Coordinator Server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description coordinator
Druid Coordinator Server

%package middlemanager
Summary: Druid MiddleManager Server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description middlemanager
Druid MiddleManager Server

%package overlord
Summary: Druid Overlord Server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description overlord
Druid Overlord Server

%package router
Summary: Druid Router Server
Group: Applications/Internet
Requires: %{name} = %{version}-%{release}

%description router
Druid Router Server


%pre
getent group druid >/dev/null || groupadd -r druid
getent passwd druid >/dev/null || \
    useradd -r -g druid -d /usr/lib/druid -s /sbin/nologin \
    -c "Druid Server Service" druid
exit 0

%prep
%setup -n %{name}-%{name}-%{version}

%build
sh %{SOURCE1}

%install
%__rm -rf %RPM_BUILD_ROOT

sh %{SOURCE2} \
	--build-dir=$PWD \
	--prefix=$RPM_BUILD_ROOT \
	--source-dir=$RPM_SOURCE_DIR

%__install -d  -m 0755  %{buildroot}/%{_localstatedir}/log/druid
%__install -d  -m 0755  %{buildroot}/%{_localstatedir}/run/druid

# Generate the init.d scripts
for service in %{druid_services}
do
       bash %{SOURCE4} $RPM_SOURCE_DIR/%{name}-${service}.svc rpm $RPM_BUILD_ROOT/%{initd_dir}/%{name}-${service}
#       cp $RPM_SOURCE_DIR/${service/-*/}.default $RPM_BUILD_ROOT/etc/default/%{name}-${service}
#       chmod 644 $RPM_BUILD_ROOT/etc/default/%{name}-${service}
done

%post
%{alternatives_cmd} --install %{etc_druid_server_conf} %{name}-conf %{etc_druid_server_conf_dist} 30

%preun
if [ "$1" = 0 ]; then
        %{alternatives_cmd} --remove %{name}-conf %{etc_druid_server_conf_dist} || :
fi

# Service file management RPMs
%define service_macro() \
%files %1 \
%defattr(-,root,root) \
%{initd_dir}/%{name}-%1 \
#%config(noreplace) /etc/default/%{name}-%1 \
%post %1 \
chkconfig --add %{name}-%1 \
\
%preun %1 \
if [ $1 = 0 ]; then \
  service %{name}-%1 stop > /dev/null 2>&1 \
  chkconfig --del %{name}-%1 \
fi \
%postun %1 \
if [ $1 -ge 1 ]; then \
  service %{name}-%1 condrestart >/dev/null 2>&1 \
fi

%service_macro broker
%service_macro coordinator
%service_macro historical 
%service_macro middlemanager
%service_macro overlord
%service_macro realtime 
%service_macro router 

%files
%defattr(-,root,root,755)
%attr(755,root,root)%{druid_server_home}/run_druid_server.sh
%defattr(-,root,root)
%{druid_server_home}/config
%{druid_server_home}/logs
%{druid_server_home}/lib
%{druid_server_home}/LICENSE
%{druid_server_home}/extensions-repo
%defattr(-,druid,druid)
%dir %{_localstatedir}/log/druid 
%dir %{_localstatedir}/run/druid
%config(noreplace)/%{etc_druid_server_conf_dist}

%files examples
%defattr(-,root,root,644)
%{druid_server_home}/examples
%defattr(-,root,root,755)
%{druid_server_home}/*example*.sh


%clean


%changelog
* Mon Feb 02 2015 Cleber Rodrigues <cleber@cleberar.com> 0.6.171-0.1
- first
