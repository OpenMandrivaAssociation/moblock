%define blocklist guarding.p2b

Name:           moblock
Version:        0.8
Release:        %mkrel 11
Epoch:          0
Summary:        Block connections from/to hosts listed in a file in peerguardian format
License:        GPL
Group:          System/Servers
URL:            http://moblock.berlios.de/
# cvs -d:pserver:anonymous@cvs.moblock.berlios.de:/cvsroot/moblock login
# cvs -z3 -d:pserver:anonymous@cvs.moblock.berlios.de:/cvsroot/moblock co moblock
Source0:        %{name}-%{version}.tar.bz2
Source1:        %{name}-blocklists-lists.blocklist.org-20060318.tar.bz2
Source2:        %{name}.init
Source3:        %{name}.cron
Source4:        %{name}-start
Source5:        %{name}-stop
Source6:        %{name}.logrotate
Source7:        %{name}.sysconfig
Source8:        %{name}.man
Patch0:         %{name}-0.8-pg2.patch
Requires:       iptables
Requires:       listtools
Requires:       p7zip
Requires(post): rpm-helper
Requires(preun): rpm-helper
Requires:       wget
BuildRequires:  iptables-devel
BuildRequires:  libnetfilter_queue-devel
BuildRequires:  libnfnetlink-devel
BuildRequires:  listtools
BuildRequires:  p7zip
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
MoBlock is a linux console application that blocks connections from/to hosts
listed in a file in peerguardian format (guarding.p2p) and since version
0.4 it supports new peerguardian 2.x files (p2p.p2b) and ipfilter.dat
files. It uses iptables ipqueue library and it is very light in resource
usage.

%prep
%setup -q -n %{name}
%patch0 -p1
%setup -q -n %{name} -T -D -a 1

%build
%{serverbuild}
%{make} CC=%{__cc} CFLAGS="-Wall -D_GNU_SOURCE -DNFQUEUE %{optflags}"

%install
%{__rm} -rf %{buildroot}

%{__mkdir_p} %{buildroot}/sbin
%{__cp} -a moblock %{buildroot}/sbin/%{name}
%{__cp} -a %{SOURCE4} %{buildroot}/sbin/moblock-start
%{__cp} -a %{SOURCE5} %{buildroot}/sbin/moblock-stop

%{__mkdir_p} %{buildroot}%{_initrddir}
%{__cp} -a %{SOURCE2} %{buildroot}%{_initrddir}/%{name}

%{__mkdir_p} %{buildroot}%{_var}/spool/%{name}
%{__cp} -a blocklists/* %{buildroot}%{_var}/spool/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}

pushd %{buildroot}%{_var}/spool/%{name} >/dev/null
for i in *.7z; do
    %{_bindir}/7za x -o. $i >/dev/null 2>&1
done
popd >/dev/null
pushd %{buildroot}%{_var}/spool/%{name}/allow >/dev/null
for i in *.7z; do
    %{_bindir}/7za x -o. $i >/dev/null 2>&1
done
popd >/dev/null
BLOCKLIST_LOCAL=
for i in %{buildroot}%{_var}/spool/%{name}/*.p2b; do
    BLOCKLIST_LOCAL="$BLOCKLIST_LOCAL $i"
done
ALLOWLIST_LOCAL=
for i in %{buildroot}%{_var}/spool/%{name}/allow/*.p2b; do
    ALLOWLIST_LOCAL="$ALLOWLIST_LOCAL -$i"
done
%{_bindir}/mergep2p -p2b2 -o %{buildroot}%{_sysconfdir}/%{blocklist} $BLOCKLIST_LOCAL $ALLOWLIST_LOCAL
%{_bindir}/find %{buildroot}%{_var}/spool/%{name} -type f ! -name '*.7z' | %{_bindir}/xargs %{__rm}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/cron.daily
%{__cp} -a %{SOURCE3} %{buildroot}%{_sysconfdir}/cron.daily/%{name}.cron

%{__mkdir_p} %{buildroot}%{_logdir}
/bin/touch %{buildroot}%{_logdir}/%{name}.log
/bin/touch %{buildroot}%{_logdir}/MoBlock.stats

%{__mkdir_p} %{buildroot}%{_sysconfdir}/logrotate.d
%{__cp} -a %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

%{__mkdir_p} %{buildroot}%{_sysconfdir}/sysconfig
%{__cp} -a %{SOURCE7} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

%{__mkdir_p} %{buildroot}%{_mandir}/man1
%{__cp} -a %{SOURCE8} %{buildroot}%{_mandir}/man1/%{name}.1

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
%attr(0755,root,root) %{_initrddir}/%{name}
%{_mandir}/man1/%{name}.1*
%config(noreplace) %{_sysconfdir}/%{blocklist}
%dir %{_var}/spool/%{name}
%config(noreplace) %{_var}/spool/%{name}/*
%attr(0755,root,root) %{_sysconfdir}/cron.daily/%{name}.cron
%ghost %attr(0600,root,root) %{_logdir}/%{name}.log
%ghost %attr(0600,root,root) %{_logdir}/MoBlock.stats
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}
