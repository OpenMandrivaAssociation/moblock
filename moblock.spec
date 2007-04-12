Name:           moblock
Version:        0.8
Release:        %mkrel 2
Epoch:          0
Summary:        Block connections from/to hosts listed in a file in peerguardian format
URL:            http://moblock.berlios.de/
# cvs -d:pserver:anonymous@cvs.moblock.berlios.de:/cvsroot/moblock login
# cvs -z3 -d:pserver:anonymous@cvs.moblock.berlios.de:/cvsroot/moblock co moblock
Source0:        %{name}-%{version}.tar.bz2
# http://www.saunalahti.fi/~zolord/bluetack
Source1:        %{name}-blocklists.tar.bz2
Source2:        %{name}.init
Source3:        %{name}.cron
Source4:        %{name}-start
Source5:        %{name}-stop
Source6:        %{name}.logrotate
Source7:        %{name}.sysconfig
License:        GPL
Group:          System/Servers
Requires:       gzip
Requires:       iptables
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:       wget
BuildRequires:  iptables-devel
BuildRequires:  libnetfilter_queue-devel
BuildRequires:  libnfnetlink-devel
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
MoBlock is a linux console application that blocks connections from/to hosts
listed in a file in peerguardian format (guarding.p2p) and since version
0.4 it supports new peerguardian 2.x files (p2p.p2b) and ipfilter.dat
files. It uses iptables ipqueue library and it is very light in resource
usage.

%prep
%setup -q -n %{name}
%setup -q -n %{name} -T -D -a 1

%build
%serverbuild
%make CC=%{__cc} CFLAGS="-Wall -D_GNU_SOURCE -DNFQUEUE %{optflags}"

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}/sbin
%{__install} -m 755 moblock %{buildroot}/sbin/%{name}
%{__install} -m 755 %{SOURCE4} %{buildroot}/sbin/moblock-start
%{__install} -m 755 %{SOURCE5} %{buildroot}/sbin/moblock-stop

%{__mkdir_p} %{buildroot}%{_initrddir}
%{__install} -m 755 %{SOURCE2} %{buildroot}%{_initrddir}/%{name}

%{__mkdir_p} %{buildroot}%{_var}/spool/%{name}
%{__install} -m 644 blocklists/* %{buildroot}%{_var}/spool/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}
%{__cat} %{buildroot}%{_var}/spool/%{name}/* > %{buildroot}%{_sysconfdir}/guarding.p2p

%{__mkdir_p} %{buildroot}%{_sysconfdir}/cron.daily
%{__install} -m 755 %{SOURCE3} %{buildroot}%{_sysconfdir}/cron.daily/%{name}.cron

%{__mkdir_p} %{buildroot}%{_logdir}
touch %{buildroot}%{_logdir}/%{name}.log
touch %{buildroot}%{_logdir}/MoBlock.stats

%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__install} -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__install} -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%clean
%{__rm} -rf %{buildroot}

%post
%create_ghostfile %{_logdir}/%{name}.log root root 0600
%create_ghostfile %{_logdir}/MoBlock.stats root root 0600
%_post_service %{name}

%preun
%_preun_service %{name}

%files
%defattr(0644,root,root,0755)
%doc Changelog COPYING README
%attr(0755,root,root) /sbin/%{name}
%attr(0755,root,root) /sbin/%{name}-start
%attr(0755,root,root) /sbin/%{name}-stop
%config(noreplace) %attr(0755,root,root) %{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/guarding.p2p
%dir %{_var}/spool/%{name}
%config(noreplace) %{_var}/spool/%{name}/*
%config(noreplace) %attr(0755,root,root) %{_sysconfdir}/cron.daily/%{name}.cron
%ghost %attr(0600,root,root) %{_logdir}/%{name}.log
%ghost %attr(0600,root,root) %{_logdir}/MoBlock.stats
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}


