%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?pyver: %define pyver %(%{__python} -c "import sys ; print sys.version[:3]")}
%{!?branch: %define branch %(echo "$Format: .%at.%d$"| sed -e 's/[()$]//g' | awk '{print $(NF-1) $NF}' | grep -v master)}

Name:           beaker
Version:        0.4.72
Release:        0%{?branch}%{?dist}
Summary:        Filesystem layout for Beaker
Group:          Applications/Internet
License:        GPLv2+
URL:            http://fedorahosted.org/beaker
Source0:        http://fedorahosted.org/releases/b/e/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python-setuptools
BuildRequires:  python-setuptools-devel
BuildRequires:  python-devel
BuildRequires:  TurboGears


%package client
Summary:        Client component for talking to Beaker server
Group:          Applications/Internet
Requires:       python
Requires:       kobo-client
Requires:	python-setuptools


%package server
Summary:       Server component of Beaker
Group:          Applications/Internet
Requires:       TurboGears
Requires:       intltool
Requires:       python-decorator
Requires:       python-xmltramp
Requires:       python-ldap
Requires:       mod_wsgi
Requires:       python-tgexpandingformwidget
Requires:       httpd
Requires:       python-krbV


%package lab-controller
Summary:        Lab Controller xmlrpc server
Group:          Applications/Internet
Requires:       python
Requires:       mod_python
Requires:       httpd
Requires:       cobbler >= 1.4
Requires:       yum-utils
Requires:       /sbin/fenced
Requires:       telnet
Requires:       python-cpio
Requires:       kobo-client
Requires:	python-setuptools
Requires:       python-xmltramp

%package lib
Summary:        Test Library
Group:          QA
Obsoletes:      rhtslib
Provides:       rhtslib
Obsoletes:      beakerlib
Provides:       beakerlib

%description
Filesystem layout for beaker

%description client
This is the command line interface used to interact with the Beaker Server.


%description server
To Be Filled in - Server Side..


%description lab-controller
This is the interface to link Medusa and Cobbler together. Mostly provides
snippets and kickstarts.


%description lib
The beakerlib project means to provide a library of various helpers,
which could be used when writing Beaker tests.

%prep
%setup -q

%build
[ "$RPM_BUILD_ROOT" != "/" ] && [ -d $RPM_BUILD_ROOT ] && rm -rf $RPM_BUILD_ROOT;
DESTDIR=$RPM_BUILD_ROOT make

%install
DESTDIR=$RPM_BUILD_ROOT make install
ln -s RedHatEnterpriseLinux6.ks $RPM_BUILD_ROOT/var/lib/cobbler/kickstarts/redhat6.ks
ln -s Fedora.ks $RPM_BUILD_ROOT/var/lib/cobbler/kickstarts/Fedoradevelopment.ks

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{python_sitelib}/%{name}/__init__.py*
%{python_sitelib}/%{name}-%{version}-*
%{python_sitelib}/%{name}-%{version}-py%{pyver}.egg-info/

%files server
%defattr(-,root,root,-)
%doc Server/README COPYING
%{python_sitelib}/%{name}/server/
%{python_sitelib}/%{name}.server-%{version}-*
%{python_sitelib}/%{name}.server-%{version}-py%{pyver}.egg-info/
%{_bindir}/start-%{name}
%{_bindir}/%{name}-init
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}-server.conf
%attr(-,apache,root) %{_datadir}/%{name}
%attr(-,apache,root) %config(noreplace) %{_sysconfdir}/%{name}/server.cfg
%attr(-,apache,root) %dir %{_localstatedir}/log/%{name}

%files client
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/beaker/client.conf
%{python_sitelib}/%{name}/client/
%{python_sitelib}/%{name}.client-%{version}-*
%{python_sitelib}/%{name}.client-%{version}-py%{pyver}.egg-info/
%{_bindir}/beaker-client

%files lab-controller
%defattr(-,root,root,-)
%doc LabController/README
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}-lab-controller.conf
%{_sysconfdir}/cron.daily/expire_distros
/var/lib/cobbler/triggers/sync/post/osversion.trigger
/var/lib/cobbler/snippets/*
/var/lib/cobbler/kickstarts/*
/var/www/beaker/rhts-checkin

%files lib
/usr/lib/beakerlib/*
/usr/share/beakerlib/*
/usr/share/rhts-library/*
/usr/share/man/man1/beakerlib*

%changelog
* Tue Dec 22 2009 Bill Peck <bpeck@redhat.com> - 0.4.70-0
- another fix to the release_action code. send proper action methods
  to cobbler, Off->off On->on.
* Thu Dec 17 2009 Bill Peck <bpeck@redhat.com> - 0.4.69-0
- small fix for release action, default to power off.
* Fri Dec 11 2009 Bill Peck <bpeck@redhat.com> - 0.4.68-0
- osversion now knows what arches are expected for that update.
  This allows us to only tag distros as STABLE if all arches are imported and tagged as INSTALLS
- update distro-list command to show the distro name, suitable for feeding into workflows.
* Wed Dec 09 2009 Bill Peck <bpeck@redhat.com> - 0.4.67-0
- Raymonds fix for is_not in arch search
- additional fixes from Raymond
- fix for beaker-init to create ReleaseAction Table
* Sun Dec 06 2009 Bill Peck <bpeck@redhat.com> - 0.4.65-0
- New ReleaseAction code, allows systems to stay on or
  reprovision at time of return.
* Tue Dec 01 2009 Bill Peck <bpeck@redhat.com> - 0.4.64-0
- Fix ISE in simplesearch
- added PATH=/usr/bin:$PATH to rhel3 kickstart
* Fri Nov 20 2009 Bill Peck <bpeck@redhat.com> - 0.4.63-0
- merged Raymond's Key/Value search ability
* Fri Nov 20 2009 Bill Peck <bpeck@redhat.com> - 0.4.62-1
- Fixes for searching drivers
- Random selection when more than one host available.
* Tue Nov 17 2009 Bill Peck <bpeck@redhat.com> - 0.4.61-0
- Fixes for searching on cpuflags
- new manual kickstart keyword allows interactive installs
* Wed Oct 28 2009 Bill Peck <bpeck@redhat.com> - 0.4.57-0
- New search implemented by Raymond Mancy
- don't try and power off machines that were temporarily reserved by legacy rhts
- view groups for non admin users
* Fri Oct 16 2009 Bill Peck <bpeck@redhat.com> - 0.4.53-0
- fix allows custom kickstarts to still append packages
* Tue Oct 06 2009 Bill Peck <bpeck@redhat.com> - 0.4.52-0
- pass !key along to cobbler for further processing.
* Mon Oct 05 2009 Bill Peck <bpeck@redhat.com> - 0.4.51-0
- fix for reserve report, not all records have a Reserved action.
* Thu Oct 01 2009 Bill Peck <bpeck@redhat.com> - 0.4.50-0
- Fixed system exclude to work properly from Distro.systems()
  previously excluding one arch would exclude all.
- added first report. reserve, shows length of currently reserved systems
- updated reserve report to honor NDA/secret settings.
* Wed Sep 30 2009 Petr Muller <pmuller@redhat.com> - 0.4.46-0
- backported few beakerlib fixes from the development branch
* Wed Sep 29 2009 Bill Peck <bpeck@redhat.com> - 0.4.45-0
- updated rhts-checkin to report anaconda logs to legacy rhts.
* Tue Sep 15 2009 Bill Peck <bpeck@redhat.com> - 0.4.44-0
- fixed wrong default language for Fedora kickstarts
- attempted to make broken search a little better.
* Thu Sep 10 2009 Bill Peck <bpeck@redhat.com> - 0.4.43-0
- added RHEL6/F12 package groups for development
* Thu Sep 03 2009 Bill Peck <bpeck@redhat.com> - 0.4.42-0
- fixed saving tag Activity on Distro.
* Thu Aug 27 2009 Bill Peck <bpeck@redhat.com> - 0.4.41-0
- use action_release() in controllers
* Thu Aug 27 2009 Bill Peck <bpeck@redhat.com> - 0.4.40-0
- option to not wait for power commands if talking to cobbler 1.7 or newer
* Tue Aug 25 2009 Bill Peck <bpeck@redhat.com> - 0.4.39-7
- re-worked remote calls to cobbler to be in their own sub-class.
  This was needed to support the latest version of cobbler.
- added not_anonymous tags around distro tagi add/remove methods.
* Fri Aug 21 2009 Petr Muller <pmuller@redhat.com> - 0.4.39-0
- cherry picked fixes from master branch for beakerlib:
- various doc fixes
- tweaked phase reporting 
- new options & functionality for rlRun
- enabling manual use of journal comparator
- new rlPass and rlFail functions
- new rlSendFile function
- plugin mechanism
- xml character breakage fix
* Thu Aug 20 2009 Bill Peck <bpeck@redhat.com> - 0.4.38-0
- Allow skipx in kickstarts to be passed in from metadata.
- Added xmlrpc method for editing distro Update.
* Wed Aug 12 2009 Bill Peck <bpeck@redhat.com> - 0.4.37-0
- Escape $ in custom kickstarts sent to cobbler
* Tue Aug 11 2009 Bill Peck <bpeck@redhat.com> - 0.4.36-0
- create subprofile
* Mon Aug 10 2009 Bill Peck <bpeck@redhat.com> - 0.4.34-0
- Change how custom kickstarts are handled. Don't copy
  cobbler profiles anymore, just use system profile and set
  parent if needed.
* Fri Aug 07 2009 Bill Peck <bpeck@redhat.com> - 0.4.33-0
- Allow the owner of a system to force a loan return.
* Wed Aug 05 2009 Bill Peck <bpeck@redhat.com> - 0.4.32-0
- Require users to be logged in to do actions and saves.
  This forces an automatic relogin if using kerberos.
* Tue Aug 04 2009 Bill Peck <bpeck@redhat.com> - 0.4.31-0
- fixed remove_distro call in expire distros
* Mon Aug 03 2009 Bill Peck <bpeck@redhat.com> - 0.4.30-0
- Updated osversion.trigger to not traceback when encountering an 
  unknown compressor.
* Tue Jul 28 2009 Bill Peck <bpeck@redhat.com> - 0.4.29-0
- Changes cobbler scripts to do everything through xmlrpc.
  cobbler gets confused otherwiese.
* Fri Jul 24 2009 Bill Peck <bpeck@redhat.com> - 0.4.28-0
- Fixed string_to_hash to not barf on extra spaces
* Mon Jul 20 2009 Bill Peck <bpeck@redhat.com> - 0.4.27-0
- Expanded user_name field to 255 chars.
* Mon Jul 20 2009 Bill Peck <bpeck@redhat.com> - 0.4.26-0
- Enable ntp in cobbler snippets
* Fri Jul 17 2009 Bill Peck <bpeck@redhat.com> - 0.4.25-0
- Fixed system arch filtering to be unicode not int.
* Thu Jul 16 2009 Bill Peck <bpeck@redhat.com> - 0.4.24-0
- Allow systems to query on arch even though we are already starting
  from a distro.  This allows you to ask for systems that are not x86_64
  for example.
- Don't fail if we can't power off a system when returning it.
- Use correct username when returning a system to the pool.
- Remove --resolvedeps from RHEL6 kickstart file.
* Tue Jul 14 2009 Bill Peck <bpeck@redhat.com> - 0.4.22-0
- Fix distro_method value to be unicode instead of boolean.
* Mon Jul 13 2009 Bill Peck <bpeck@redhat.com> - 0.4.21-0
- Allow legacy RHTS to ask for distros based on install method
* Tue Jul 07 2009 Bill Peck <bpeck@redhat.com> - 0.4.20-0
- Include Workstation key for RedHatEnterpriseLinuxClient5
* Mon Jul 06 2009 Bill Peck <bpeck@redhat.com> - 0.4.19-0
- Don't populate runtest_url in ks_meta if its not defined.
* Wed Jul 01 2009 Bill Peck <bpeck@redhat.com> - 0.4.18-2
- Use RUNTEST_URL from rhts if passed.
- Include Fedoradevelopment.ks for rawhide
* Tue Jun 30 2009 Bill Peck <bpeck@redhat.com> - 0.4.17-0
- Call the correct method for _tag
* Tue Jun 30 2009 Bill Peck <bpeck@redhat.com> - 0.4.16-0
- update login_krbv method for newer kobo package
* Tue Jun 30 2009 Bill Peck <bpeck@redhat.com> - 0.4.15-0
- Call addDistros.sh from osversion.trigger if it exists.
* Mon Jun 29 2009 Bill Peck <bpeck@redhat.com> - 0.4.14-0
- Allow searching by treepath for command line client
- return distro name for legacy rhts.
* Mon Jun 22 2009 Bill Peck <bpeck@redhat.com> - 0.4.13-0
- Fixed osversion.trigger to work with methods other than nfs
* Fri Jun 19 2009 Bill Peck <bpeck@redhat.com> - 0.4.12-0
- Raise BeakerExceptions if we run into trouble
* Thu Jun 18 2009 Bill Peck <bpeck@redhat.com> - 0.4.11-0
- added install_name to distro pick method
- fixed 500 error when non-admin adds a new system with shared set.
* Fri Jun 12 2009 Bill Peck <bpeck@redhat.com> - 0.4.9-1
- releng fixed the name of rhel6 to RedHatEnterpriseLinux6 in .treeinfo
* Wed Jun 10 2009 Bill Peck <bpeck@redhat.com> - 0.4.9
- Added simple json method for tagging distros as Installable.
- Added RHEL6 kickstart file.
* Wed Jun 03 2009 Bill Peck <bpeck@redhat.com> - 0.4.8
- Catch xmlrpc errors from cobbler and record/display them
* Mon Jun 01 2009 Bill Peck <bpeck@redhat.com> - 0.4.7
- added distros list,tag,untag to beaker-client
- fixed some minor issues with the xmlrpc interface.
* Thu May 28 2009 Bill Peck <bpeck@redhat.com> - 0.4.6
- Clear systems console log via xmlrpc
* Thu May 28 2009 Bill Peck <bpeck@redhat.com> - 0.4.5
- free and available views will only show working systems now.
* Tue May 26 2009 Bill Peck <bpeck@redhat.com> - 0.4.4
- Fixed missing power_id from CSV import/export
- Use $default_password_crypted from /etc/cobbler/settings unless $password 
  is set.
* Fri May 22 2009 Bill Peck <bpeck@redhat.com> - 0.4.2
- Added in beakerlib sub package
- Fixed tempfile close in osversion.trigger
* Thu May 21 2009 Bill Peck <bpeck@redhat.com> - 0.4-3
- fix power import
* Tue May 19 2009 Bill Peck <bpeck@redhat.com> - 0.4-1
- Major reworking of directory layout.
* Tue May 12 2009 Bill Peck <bpeck@redhat.com> - 0.3-1
- First stab at client interface
