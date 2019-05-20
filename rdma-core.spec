%{!?cmake: %global cmake cmake}
%{!?_udevrulesdir: %global _udevrulesdir /etc/udev/rules.d}

# if systemd not supported, do not install the systemd service files
%{!?_unitdir: %global _unitdir NA}
%global HAVE_LIBUDEV %(if ( /bin/ls /usr/lib*/libudev*so &> /dev/null); then echo -n '1'; else echo -n '0'; fi)
%global WITH_SYSTEMD %(if ( test -d "%{_unitdir}" > /dev/null); then echo -n '1'; else echo -n '0'; fi)

Name: rdma-core
Version: 46mlnx2
Release: 1%{?dist}
Summary: RDMA core userspace libraries and daemons
Group: System Environment/Libraries

# Almost everything is licensed under the OFA dual GPLv2, 2 Clause BSD license
#  providers/ipathverbs/ Dual licensed using a BSD license with an extra patent clause
#  providers/rxe/ Incorporates code from ipathverbs and contains the patent clause
#  providers/hfi1verbs Uses the 3 Clause BSD license
License: GPLv2 or BSD
Url: https://github.com/linux-rdma/rdma-core
Source: rdma-core-%{version}.tgz
# Do not build static libs by default.
%define with_static 1
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX)

BuildRequires: binutils
BuildRequires: cmake >= 2.8.11
BuildRequires: gcc
BuildRequires: libudev-devel
BuildRequires: pkgconfig
BuildRequires: pkgconfig(libnl-3.0)
BuildRequires: pkgconfig(libnl-route-3.0)
%define with_pyverbs %{?_with_pyverbs: 1} %{?!_with_pyverbs: 0}
%if %{with_pyverbs}
BuildRequires: python3-devel
BuildRequires: python3-Cython
%else
BuildRequires: python
%endif

# Red Hat/Fedora previously shipped redhat/ as a stand-alone
# package called 'rdma', which we're supplanting here.
Provides: rdma = %{version}-%{release}
Obsoletes: rdma < %{version}-%{release}
Provides: rdma-ndd = %{version}-%{release}
Obsoletes: rdma-ndd < %{version}-%{release}
# the ndd utility moved from infiniband-diags to rdma-core
Conflicts: infiniband-diags <= 1.6.7
Requires: pciutils
# 32-bit arm is missing required arch-specific memory barriers,
ExcludeArch: %{arm}

%define CMAKE_FLAGS %{nil}
%if 0%{?suse_version}
# Tumbleweed's cmake RPM macro adds -Wl,--no-undefined to the module flags
# which is totally inappropriate and breaks building 'ENABLE_EXPORTS' style
# module libraries (eg ibacmp).
%define CMAKE_FLAGS -DCMAKE_MODULE_LINKER_FLAGS=""
%endif
BuildRequires: make
%define make_jobs make %{?_smp_mflags}
%if 0%{?cmake_install:1}
%else
%define cmake_install DESTDIR=%{buildroot} make install
%endif

%if 0%{?fedora} >= 25
# pandoc was introduced in FC25
BuildRequires: pandoc
%endif

%description
RDMA core userspace infrastructure and documentation, including initialization
scripts, kernel driver-specific modprobe override configs, IPoIB network
scripts, dracut rules, and the rdma-ndd utility.

%package devel
Summary: RDMA core development libraries and headers
Group: System Environment/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libibverbs = %{version}-%{release}
Provides: libibverbs-devel = %{version}-%{release}
Obsoletes: libibverbs-devel < %{version}-%{release}
Provides: libibverbs-devel-static = %{version}-%{release}
Obsoletes: libibverbs-devel-static < %{version}-%{release}
Requires: libibumad = %{version}-%{release}
Provides: libibumad-devel = %{version}-%{release}
Obsoletes: libibumad-devel < %{version}-%{release}
Provides: libibumad-static = %{version}-%{release}
Obsoletes: libibumad-static < %{version}-%{release}
Requires: librdmacm = %{version}-%{release}
Provides: librdmacm-devel = %{version}-%{release}
Obsoletes: librdmacm-devel < %{version}-%{release}
Provides: librdmacm-static = %{version}-%{release}
Obsoletes: librdmacm-static < %{version}-%{release}
Requires: ibacm = %{version}-%{release}
Provides: ibacm-devel = %{version}-%{release}
Obsoletes: ibacm-devel < %{version}-%{release}
%if %{with_static}
# Since our pkg-config files include private references to these packages they
# need to have their .pc files installed too, even for dynamic linking, or
# pkg-config breaks.
BuildRequires: pkgconfig(libnl-3.0)
BuildRequires: pkgconfig(libnl-route-3.0)
%endif
Provides: libcxgb3-static = %{version}-%{release}
Obsoletes: libcxgb3-static < %{version}-%{release}
Provides: libcxgb4-static = %{version}-%{release}
Obsoletes: libcxgb4-static < %{version}-%{release}
Provides: libhfi1-static = %{version}-%{release}
Obsoletes: libhfi1-static < %{version}-%{release}
Provides: libipathverbs-static = %{version}-%{release}
Obsoletes: libipathverbs-static < %{version}-%{release}
Provides: libmlx4-devel = %{version}-%{release}
Obsoletes: libmlx4-devel < %{version}-%{release}
Provides: libmlx4-static = %{version}-%{release}
Obsoletes: libmlx4-static < %{version}-%{release}
Provides: libmlx5-devel = %{version}-%{release}
Obsoletes: libmlx5-devel < %{version}-%{release}
Provides: libmlx5-static = %{version}-%{release}
Obsoletes: libmlx5-static < %{version}-%{release}
Provides: libnes-static = %{version}-%{release}
Obsoletes: libnes-static < %{version}-%{release}
Provides: libocrdma-static = %{version}-%{release}
Obsoletes: libocrdma-static < %{version}-%{release}
Provides: libi40iw-devel-static = %{version}-%{release}
Obsoletes: libi40iw-devel-static < %{version}-%{release}
Provides: libmthca-static = %{version}-%{release}
Obsoletes: libmthca-static < %{version}-%{release}

%description devel
RDMA core development libraries and headers.

%package -n libibverbs
Summary: A library and drivers for direct userspace use of RDMA (InfiniBand/iWARP/RoCE) hardware
Group: System Environment/Libraries
Requires(post): /sbin/ldconfig
Requires(postun): /sbin/ldconfig
Requires: %{name}%{?_isa} = %{version}-%{release}
Provides: libcxgb3 = %{version}-%{release}
Obsoletes: libcxgb3 < %{version}-%{release}
Provides: libcxgb4 = %{version}-%{release}
Obsoletes: libcxgb4 < %{version}-%{release}
Provides: libhfi1 = %{version}-%{release}
Obsoletes: libhfi1 < %{version}-%{release}
Provides: libi40iw = %{version}-%{release}
Obsoletes: libi40iw < %{version}-%{release}
Provides: libipathverbs = %{version}-%{release}
Obsoletes: libipathverbs < %{version}-%{release}
Provides: libmlx4 = %{version}-%{release}
Obsoletes: libmlx4 < %{version}-%{release}
%ifnarch s390x s390
Provides: libmlx5 = %{version}-%{release}
Obsoletes: libmlx5 < %{version}-%{release}
%endif
Provides: libmthca = %{version}-%{release}
Obsoletes: libmthca < %{version}-%{release}
Provides: libnes = %{version}-%{release}
Obsoletes: libnes < %{version}-%{release}
Provides: libocrdma = %{version}-%{release}
Obsoletes: libocrdma < %{version}-%{release}
Provides: librxe = %{version}-%{release}
Obsoletes: librxe < %{version}-%{release}

%description -n libibverbs
libibverbs is a library that allows userspace processes to use RDMA
"verbs" as described in the InfiniBand Architecture Specification and
the RDMA Protocol Verbs Specification.  This includes direct hardware
access from userspace to InfiniBand/iWARP adapters (kernel bypass) for
fast path operations.

Device-specific plug-in ibverbs userspace drivers are included:

- libmlx4: Mellanox ConnectX-3 InfiniBand HCA
- libmlx5: Mellanox Connect-IB/X-4+ InfiniBand HCA
- librxe: A software implementation of the RoCE protocol

%package -n libibverbs-utils
Summary: Examples for the libibverbs library
Group: System Environment/Libraries
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n libibverbs-utils
Useful libibverbs example programs such as ibv_devinfo, which
displays information about RDMA devices.

%package -n ibacm
Summary: InfiniBand Communication Manager Assistant
Group: System Environment/Libraries

Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libibumad%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n ibacm
The ibacm daemon helps reduce the load of managing path record lookups on
large InfiniBand fabrics by providing a user space implementation of what
is functionally similar to an ARP cache.  The use of ibacm, when properly
configured, can reduce the SA packet load of a large IB cluster from O(n^2)
to O(n).  The ibacm daemon is started and normally runs in the background,
user applications need not know about this daemon as long as their app
uses librdmacm to handle connection bring up/tear down.  The librdmacm
library knows how to talk directly to the ibacm daemon to retrieve data.


%package -n libibumad
Summary: OpenFabrics Alliance InfiniBand umad (userspace management datagram) library
Group: System Environment/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description -n libibumad
libibumad provides the userspace management datagram (umad) library
functions, which sit on top of the umad modules in the kernel. These
are used by the IB diagnostic and management tools, including OpenSM.

%package -n librdmacm
Summary: Userspace RDMA Connection Manager
Group: System Environment/Libraries
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n librdmacm
librdmacm provides a userspace RDMA Communication Managment API.

%package -n librdmacm-utils
Summary: Examples for the librdmacm library
Group: System Environment/Libraries
Requires: librdmacm%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n librdmacm-utils
Example test programs for the librdmacm library.

%package -n srp_daemon
Summary: Tools for using the InfiniBand SRP protocol devices
Group: System Environment/Libraries
Obsoletes: srptools <= 1.0.3
Provides: srptools = %{version}-%{release}
Obsoletes: openib-srptools <= 0.0.6
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: libibumad%{?_isa} = %{version}-%{release}
Requires: libibverbs%{?_isa} = %{version}-%{release}

%description -n srp_daemon
In conjunction with the kernel ib_srp driver, srp_daemon allows you to
discover and use SCSI devices via the SCSI RDMA Protocol over InfiniBand.

%if %{with_pyverbs}
%package -n python3-pyverbs
Summary: Python3 API over IB verbs
%{?python_provide:%python_provide python%{python3_pkgversion}-pyverbs}

%description -n python3-pyverbs
Pyverbs is a Cython-based Python API over libibverbs, providing an
easy, object-oriented access to IB verbs.
%endif

%prep
%setup -q

%build

# New RPM defines _rundir, usually as /run
%if 0%{?_rundir:1}
%else
%define _rundir /var/run
%endif

%{!?EXTRA_CMAKE_FLAGS: %define EXTRA_CMAKE_FLAGS %{nil}}

# Pass all of the rpm paths directly to GNUInstallDirs and our other defines.
%cmake %{CMAKE_FLAGS} \
         -DCMAKE_BUILD_TYPE=Release \
         -DCMAKE_INSTALL_BINDIR:PATH=%{_bindir} \
         -DCMAKE_INSTALL_SBINDIR:PATH=%{_sbindir} \
         -DCMAKE_INSTALL_LIBDIR:PATH=%{_libdir} \
         -DCMAKE_INSTALL_LIBEXECDIR:PATH=%{_libexecdir} \
         -DCMAKE_INSTALL_LOCALSTATEDIR:PATH=%{_localstatedir} \
         -DCMAKE_INSTALL_SHAREDSTATEDIR:PATH=%{_sharedstatedir} \
         -DCMAKE_INSTALL_INCLUDEDIR:PATH=%{_includedir} \
         -DCMAKE_INSTALL_INFODIR:PATH=%{_infodir} \
         -DCMAKE_INSTALL_MANDIR:PATH=%{_mandir} \
         -DCMAKE_INSTALL_SYSCONFDIR:PATH=%{_sysconfdir} \
         -DCMAKE_INSTALL_SYSTEMD_SERVICEDIR:PATH=%{_unitdir} \
         -DCMAKE_INSTALL_INITDDIR:PATH=%{_initrddir} \
         -DCMAKE_INSTALL_RUNDIR:PATH=%{_rundir} \
         -DCMAKE_INSTALL_DOCDIR:PATH=%{_docdir}/%{name}-%{version} \
         -DCMAKE_INSTALL_UDEV_RULESDIR:PATH=%{_udevrulesdir} \
%if "%{WITH_SYSTEMD}" == "0"
         -DWITHOUT_SYSTEMD=1 \
%endif
%if %{with_static}
         -DENABLE_STATIC=1 \
%endif
%if %{with_pyverbs}
         -DNO_PYVERBS=0
%else
         -DNO_PYVERBS=1
%endif
%make_jobs

%install
%cmake_install

mkdir -p %{buildroot}/%{_sysconfdir}/rdma
%{__rm} -rf %{buildroot}/%{_sysconfdir}/rdma/modules

# ibacm
IB_ACME=bin/ib_acme
[ -e build/bin/ib_acme ] && IB_ACME=build/bin/ib_acme
LD_LIBRARY_PATH=%{buildroot}%{_libdir} ${IB_ACME} -D . -O
# multi-lib conflict resolution hacks (bug 1429362)
sed -i -e 's|%{_libdir}|/usr/lib|' %{buildroot}%{_mandir}/man7/ibacm_prov.7
sed -i -e 's|%{_libdir}|/usr/lib|' ibacm_opts.cfg
install -D -m0644 ibacm_opts.cfg %{buildroot}%{_sysconfdir}/rdma/

[ -d "%{buildroot}%{_prefix}/NA" ] && %{__rm} -rf %{buildroot}%{_prefix}/NA

# Delete the package's init.d scripts
rm -rf %{buildroot}/%{_initrddir}/
rm -rf %{buildroot}/%{_sbindir}/srp_daemon.sh

%post -n libibverbs -p /sbin/ldconfig
%postun -n libibverbs -p /sbin/ldconfig

%post -n libibumad -p /sbin/ldconfig
%postun -n libibumad -p /sbin/ldconfig

%post -n librdmacm -p /sbin/ldconfig
%postun -n librdmacm -p /sbin/ldconfig

%post -n srp_daemon
%if "%{WITH_SYSTEMD}" == "1"
%systemd_post srp_daemon.service
%endif
%preun -n srp_daemon
%if "%{WITH_SYSTEMD}" == "1"
%systemd_preun srp_daemon.service
%endif
%postun -n srp_daemon
%if "%{WITH_SYSTEMD}" == "1"
%systemd_postun_with_restart srp_daemon.service
%endif

%files
%dir %{_sysconfdir}/rdma
%dir %{_docdir}/%{name}-%{version}
%doc %{_docdir}/%{name}-%{version}/README.md
%doc %{_docdir}/%{name}-%{version}/rxe.md
%doc %{_docdir}/%{name}-%{version}/udev.md
%doc %{_docdir}/%{name}-%{version}/tag_matching.md
%{_udevrulesdir}/../rdma_rename
%{_udevrulesdir}/60-rdma-persistent-naming.rules
%config(noreplace) %{_sysconfdir}/modprobe.d/mlx4.conf
%{_sysconfdir}/udev/rules.d/70-persistent-ipoib.rules
%{_udevrulesdir}/75-rdma-description.rules
%{_udevrulesdir}/90-rdma-umad.rules
%if "%{HAVE_LIBUDEV}" == "1"
%{_udevrulesdir}/60-rdma-ndd.rules
%{_sbindir}/rdma-ndd
%if "%{WITH_SYSTEMD}" == "1"
%{_unitdir}/rdma-ndd.service
%endif
%{_mandir}/man8/rdma-ndd.*
%endif
%{_bindir}/rxe_cfg
%{_mandir}/man7/rxe*
%{_mandir}/man8/rxe*

%files devel
%doc %{_docdir}/%{name}-%{version}/MAINTAINERS
%dir %{_includedir}/infiniband
%dir %{_includedir}/rdma
%{_includedir}/infiniband/*
%{_includedir}/rdma/*
%if %{with_static}
%{_libdir}/lib*.a
%endif
%{_libdir}/lib*.so
%{_libdir}/pkgconfig/libibumad.pc
%{_libdir}/pkgconfig/libibverbs.pc
%{_libdir}/pkgconfig/libmlx4.pc
%{_libdir}/pkgconfig/libmlx5.pc
%{_libdir}/pkgconfig/librdmacm.pc
%{_mandir}/man3/ibv_*
%{_mandir}/man3/rdma*
%{_mandir}/man3/umad*
%{_mandir}/man3/*_to_ibv_rate.*
%{_mandir}/man7/rdma_cm.*
%ifnarch s390x s390
%{_mandir}/man3/mlx5dv*
%endif
%{_mandir}/man3/mlx4dv*
%ifnarch s390x s390
%{_mandir}/man7/mlx5dv*
%endif
%{_mandir}/man7/mlx4dv*

%files -n libibverbs
%dir %{_sysconfdir}/libibverbs.d
%dir %{_libdir}/libibverbs
%{_libdir}/libibverbs*.so.*
%{_libdir}/libibverbs/*.so
%ifnarch s390x s390
%{_libdir}/libmlx5.so.*
%endif
%{_libdir}/libmlx4.so.*
%config(noreplace) %{_sysconfdir}/libibverbs.d/*.driver
%doc %{_docdir}/%{name}-%{version}/libibverbs.md

%files -n libibverbs-utils
%{_bindir}/ibv_*
%{_mandir}/man1/ibv_*

%files -n ibacm
%config(noreplace) %{_sysconfdir}/rdma/ibacm_opts.cfg
%{_bindir}/ib_acme
%{_sbindir}/ibacm
%{_mandir}/man1/ibacm.*
%{_mandir}/man1/ib_acme.*
%{_mandir}/man7/ibacm.*
%{_mandir}/man7/ibacm_prov.*
%dir %{_libdir}/ibacm
%{_libdir}/ibacm/*
%doc %{_docdir}/%{name}-%{version}/ibacm.md


%files -n libibumad
%{_libdir}/libibumad*.so.*

%files -n librdmacm
%{_libdir}/librdmacm*.so.*
%dir %{_libdir}/rsocket
%{_libdir}/rsocket/*.so*
%doc %{_docdir}/%{name}-%{version}/librdmacm.md
%{_mandir}/man7/rsocket.*

%files -n librdmacm-utils
%{_bindir}/cmtime
%{_bindir}/mckey
%{_bindir}/rcopy
%{_bindir}/rdma_client
%{_bindir}/rdma_server
%{_bindir}/rdma_xclient
%{_bindir}/rdma_xserver
%{_bindir}/riostream
%{_bindir}/rping
%{_bindir}/rstream
%{_bindir}/ucmatose
%{_bindir}/udaddy
%{_bindir}/udpong
%{_mandir}/man1/cmtime.*
%{_mandir}/man1/mckey.*
%{_mandir}/man1/rcopy.*
%{_mandir}/man1/rdma_client.*
%{_mandir}/man1/rdma_server.*
%{_mandir}/man1/rdma_xclient.*
%{_mandir}/man1/rdma_xserver.*
%{_mandir}/man1/riostream.*
%{_mandir}/man1/rping.*
%{_mandir}/man1/rstream.*
%{_mandir}/man1/ucmatose.*
%{_mandir}/man1/udaddy.*
%{_mandir}/man1/udpong.*

%files -n srp_daemon
%config(noreplace) %{_sysconfdir}/srp_daemon.conf
%{_libexecdir}/srp_daemon/start_on_all_ports
%if "%{WITH_SYSTEMD}" == "1"
%{_unitdir}/srp_daemon.service
%{_unitdir}/srp_daemon_port@.service
%endif
%{_sbindir}/ibsrpdm
%{_sbindir}/srp_daemon
%{_sbindir}/run_srp_daemon
%{_udevrulesdir}/60-srp_daemon.rules
%{_mandir}/man1/ibsrpdm.1*
%{_mandir}/man1/srp_daemon.1*
%{_mandir}/man5/srp_daemon.service.5*
%{_mandir}/man5/srp_daemon_port@.service.5*
%doc %{_docdir}/%{name}-%{version}/ibsrpdm.md
%if %{with_pyverbs}
%files -n python3-pyverbs
%{python3_sitearch}/pyverbs
%endif

