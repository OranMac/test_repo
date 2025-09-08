%global disable_toolsets  0

%ifarch %{ix86}
  # no debug package for the i686 because oom on i686 with debuginfos
  #FIXME revise if still necessary
  %global debug_package %{nil}
%endif

%{lua:
function dist_to_rhel_minor(str, start)
  match = string.match(str, ".module%+el8.%d+")
  if match then
     return string.sub(match, 13)
  end
  match = string.match(str, ".el8_%d+")
  if match then
     return string.sub(match, 6)
  end
  match = string.match(str, ".el8")
  if match then
     return 6
  end
  return -1
end}

%global rhel_minor_version %{lua:print(dist_to_rhel_minor(rpm.expand("%dist")))}
%global build_with_clang  0

%global system_nss        1
%global bundle_nss        0

%if 0%{?rhel} == 8
  %if %{rhel_minor_version} < 3
    %global bundle_nss        1
    %global system_nss        1
  %endif
%endif

%define use_bundled_ffi   0

%global use_llvmts        0
%global use_nodejsts      0
%if 0%{?rhel} < 8
%global use_llvmts        1
%global use_nodejsts      1
%endif

%global nodejs_rb         nodejs
%global llvm_version      7.0

%if 0%{?rhel} == 8
%global llvm_version      6.0
%endif

%if 0%{?rhel} == 7
  %global use_dts         1
  %global nodejs_rb       rh-nodejs10-nodejs
  %global llvm_version    11.0
%endif

%global use_rustts        1
%if 0%{?rhel} >= 9
  %global use_rustts      0
%endif

%global dts_version       10
%global rust_version      1.52

%if 0%{?disable_toolsets}
%global use_rustts        0
%global use_dts           0
%global use_llvmts        0
%endif

# Big endian platforms
%ifarch ppc64 s390x
# Javascript Intl API is not supported on big endian platforms right now:
# https://bugzilla.mozilla.org/show_bug.cgi?id=1322212
%global big_endian        1
%endif

# Hardened build?
%global hardened_build    1

%ifarch %{ix86} x86_64
%global run_tests         0
%else
%global run_tests         0
%endif

# Build as a debug package?
%global debug_build       0

# We need to use full path because of flatpak where datadir is /app/share
%global default_bookmarks_file  /usr/share/bookmarks/default-bookmarks.html
%global firefox_app_id  \{ec8030f7-c20a-464f-9b0e-13a3a9e97384\}
# Minimal required versions

%if 0%{?system_nss}
%global nspr_version 4.32
# NSS/NSPR quite often ends in build override, so as requirement the version
# we're building against could bring us some broken dependencies from time to time.
#%global nspr_build_version %(pkg-config --silence-errors --modversion nspr 2>/dev/null || echo 65536)
%global nspr_build_version %{nspr_version}
%global nss_version 3.67
#%global nss_build_version %(pkg-config --silence-errors --modversion nss 2>/dev/null || echo 65536)
%global nss_build_version %{nss_version}
%endif

# GTK3 bundling
%define avoid_bundled_rebuild   0

%define bundled_install_path %{mozappdir}/bundled

# We could use %%include, but in %%files, %%post and other sections, but in these
# sections it could lead to syntax errors about unclosed %%if. Work around it by
# using the following macro
%define include_file() %{expand:%(cat '%1')}

%global mozappdir     %{_libdir}/%{name}
%global mozappdirdev  %{_libdir}/%{name}-devel-%{version}
%global langpackdir   %{mozappdir}/langpacks
%global tarballdir    %{name}-%{version}
%global pre_version   esr

%global official_branding       1
%global build_langpacks         1

Summary:        Mozilla Firefox Web browser
Name:           firefox
Version:        91.8.0
Release:        1%{?dist}
URL:            https://www.mozilla.org/firefox/
License:        MPLv1.1 or GPLv2+ or LGPLv2+
%if 0%{?rhel} == 9
ExcludeArch:    %{ix86}
%endif
%if 0%{?rhel} == 8
  %if %{rhel_minor_version} == 1
ExcludeArch:    %{ix86} aarch64 s390x
  %else
ExcludeArch:    %{ix86}
  %endif
%endif
%if 0%{?rhel} == 7
ExcludeArch:    aarch64 s390 ppc
%endif

# We can't use the official tarball as it contains some test files that use
# licenses that are rejected by Red Hat Legal.
# The official tarball has to be always processed by the process-official-tarball
# script.
# Link to official tarball: https://hg.mozilla.org/releases/mozilla-release/archive/firefox-%%{version}%%{?pre_version}.source.tar.xz
Source0:        firefox-%{version}%{?pre_version}.processed-source.tar.xz
%if %{build_langpacks}
Source1:        firefox-langpacks-%{version}%{?pre_version}-20220405.tar.xz

%endif
Source2:        cbindgen-vendor.tar.xz
Source3:        process-official-tarball
Source10:       firefox-mozconfig
%if 0%{?centos}
Source12:       firefox-centos-default-prefs.js
%else
Source12:       firefox-redhat-default-prefs.js
%endif
Source20:       firefox.desktop
Source21:       firefox.sh.in
Source23:       firefox.1
Source24:       mozilla-api-key
Source25:       firefox-symbolic.svg
Source26:       distribution.ini
Source27:       google-api-key
Source28:       node-stdout-nonblocking-wrapper

Source403:      nss-3.67.0-7.el8_1.src.rpm
Source401:      nss-setup-flags-env.inc
Source402:      nspr-4.32.0-1.el8_1.src.rpm

# Build patches
Patch1001:      build-ppc64le-inline.patch
Patch1008:        build-rhel7-nasm-dwarf.patch
Patch1009:        build-debuginfo-fix.patch
# workaround for https://bugzilla.redhat.com/show_bug.cgi?id=1699374
Patch4:         build-mozconfig-fix.patch
Patch6:         build-nss-version.patch

# Fedora/RHEL specific patches
Patch215:        firefox-enable-addons.patch
Patch219:        rhbz-1173156.patch
Patch224:        mozilla-1170092.patch
Patch225:        firefox-nss-addon-hack.patch

# Upstream patches

Patch503:        mozilla-s390-context.patch
Patch505:        mozilla-bmo1005535.patch
Patch506:        mozilla-bmo1504834-part1.patch
Patch507:        mozilla-bmo1504834-part2.patch
Patch508:        mozilla-bmo1504834-part3.patch
Patch509:        mozilla-bmo1504834-part4.patch
Patch510:        mozilla-bmo1554971.patch
Patch511:        mozilla-bmo1602730.patch
Patch512:        mozilla-bmo849632.patch
Patch513:        mozilla-bmo998749.patch
Patch514:        mozilla-s390x-skia-gradient.patch
Patch515:        mozilla-bmo1626236.patch
Patch518:        D110204-fscreen.diff
Patch519:        expat-CVE-2022-25235.patch
Patch520:        expat-CVE-2022-25236.patch
Patch521:        expat-CVE-2022-25315.patch

# Flatpak patches

%if %{?system_nss}
%if !0%{?bundle_nss}
BuildRequires:  pkgconfig(nspr) >= %{nspr_version}
BuildRequires:  pkgconfig(nss) >= %{nss_version}
BuildRequires:  nss-static >= %{nss_version}
%endif
%endif
BuildRequires:  pkgconfig(libpng)
BuildRequires:  xz
BuildRequires:  libXt-devel
BuildRequires:  mesa-libGL-devel
Requires:       liberation-fonts-common
Requires:       liberation-sans-fonts
BuildRequires:  libjpeg-devel
BuildRequires:  zip
BuildRequires:  bzip2-devel
BuildRequires:  pkgconfig(zlib)
#BuildRequires:  pkgconfig(libIDL-2.0)
BuildRequires:  pkgconfig(gtk+-2.0)
BuildRequires:  krb5-devel
BuildRequires:  pkgconfig(pango)
BuildRequires:  pkgconfig(freetype2) >= 2.1.9
BuildRequires:  pkgconfig(xt)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(libstartup-notification-1.0)
BuildRequires:  pkgconfig(libnotify)
BuildRequires:  pkgconfig(dri)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  dbus-glib-devel
BuildRequires:  m4

BuildRequires:  pkgconfig(libpulse)

%if 0%{?use_dts}
BuildRequires:  devtoolset-%{dts_version}-gcc-c++
BuildRequires:  devtoolset-%{dts_version}-gcc
BuildRequires:  devtoolset-%{dts_version}-libatomic-devel
%endif
%if 0%{?rhel} == 9
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  clang clang-libs llvm
%endif

BuildRequires:  scl-utils
BuildRequires:  findutils

BuildRequires:  %{nodejs_rb} >= 10.21
BuildRequires:  python3

%if 0%{?rhel} == 8
BuildRequires:  cargo
BuildRequires:  rust >= %{rust_version}
BuildRequires:  llvm >= %{llvm_version}
BuildRequires:  llvm-devel >= %{llvm_version}
BuildRequires:  clang >= %{llvm_version}
BuildRequires:  clang-devel >= %{llvm_version}
BuildRequires:  rustfmt >= %{rust_version}
%else
%if 0%{?use_rustts}
BuildRequires:  rust-toolset-%{rust_version}
%endif
%if 0%{?use_llvmts}
BuildRequires:  llvm-toolset-%{llvm_version}
BuildRequires:  llvm-toolset-%{llvm_version}-llvm-devel
BuildRequires:  llvm-toolset-%{llvm_version}-clang
BuildRequires:  llvm-toolset-%{llvm_version}-clang-devel
%endif
%endif

BuildRequires:  nasm
%if %{build_with_clang}
BuildRequires:  lld
%endif

%if 0%{?rhel} == 8
  %if %{rhel_minor_version} >= 3
BuildRequires:  pkgconfig(libpipewire-0.3)
  %else
BuildRequires:  pipewire-devel
  %endif
%endif

BuildRequires:        gtk3-devel
BuildRequires:        glib2-devel
BuildRequires:        perl-interpreter

# Bundled nss/nspr requirement
%if 0%{?bundle_nss}
BuildRequires:    nss-softokn
BuildRequires:    sqlite-devel
BuildRequires:    zlib-devel
BuildRequires:    pkgconfig
BuildRequires:    gawk
BuildRequires:    psmisc
BuildRequires:    perl-interpreter
BuildRequires:    gcc-c++
BuildRequires:    xmlto
%endif

BuildRequires:    libstdc++-static

Requires:       mozilla-filesystem
Requires:       p11-kit-trust
%if %{?system_nss}
%if !0%{?bundle_nss}
Requires:       nspr >= %{nspr_build_version}
Requires:       nss >= %{nss_build_version}
%endif
%endif

BuildRequires:  desktop-file-utils
BuildRequires:  system-bookmarks
Requires:       redhat-indexhtml

%if %{?run_tests}
BuildRequires:  xorg-x11-server-Xvfb
%endif

BuildRequires:  pkgconfig(libffi)

%if 0%{?big_endian}
  %if 0%{?flatpak}
BuildRequires:  icu
  %endif
%endif

Obsoletes:      mozilla <= 37:1.7.13
Provides:       webclient

# Bundled libraries
Provides: bundled(angle)
Provides: bundled(cairo)
Provides: bundled(graphite2)
Provides: bundled(harfbuzz)
Provides: bundled(ots)
Provides: bundled(sfntly)
Provides: bundled(skia)
Provides: bundled(thebes)
Provides: bundled(WebRender)
Provides: bundled(audioipc-2)
Provides: bundled(ffvpx)
Provides: bundled(kissfft)
Provides: bundled(libaom)
Provides: bundled(libcubeb)
Provides: bundled(libdav1d)
Provides: bundled(libjpeg)
Provides: bundled(libmkv)
Provides: bundled(libnestegg)
Provides: bundled(libogg)
Provides: bundled(libopus)
Provides: bundled(libpng)
Provides: bundled(libsoundtouch)
Provides: bundled(libspeex_resampler)
Provides: bundled(libtheora)
Provides: bundled(libtremor)
Provides: bundled(libvorbis)
Provides: bundled(libvpx)
Provides: bundled(libwebp)
Provides: bundled(libyuv)
Provides: bundled(mp4parse-rust)
Provides: bundled(mtransport)
Provides: bundled(openmax_dl)
Provides: bundled(double-conversion)
Provides: bundled(brotli)
Provides: bundled(fdlibm)
Provides: bundled(freetype2)
Provides: bundled(libmar)
Provides: bundled(woff2)
Provides: bundled(xz-embedded)
Provides: bundled(zlib)
Provides: bundled(expat)
Provides: bundled(msgpack-c)
Provides: bundled(libprio)
Provides: bundled(rlbox_sandboxing_api)
Provides: bundled(sqlite3)

%if 0%{?bundle_nss}
Provides: bundled(nss) = 3.67.0
Provides: bundled(nspr) = 4.32.0
%endif

%description
Mozilla Firefox is an open-source web browser, designed for standards
compliance, performance and portability.

%if %{run_tests}
%global testsuite_pkg_name mozilla-%{name}-testresults
%package -n %{testsuite_pkg_name}
Summary: Results of testsuite
%description -n %{testsuite_pkg_name}
This package contains results of tests executed during build.
%files -n %{testsuite_pkg_name}
/test_results
%endif

#---------------------------------------------------------------------
%prep
echo "Build environment"
echo "dist                  %{?dist}"
echo "RHEL 8 minor version: %{rhel_minor_version}"
echo "use_bundled_ffi       %{?use_bundled_ffi}"
echo "bundle_nss            %{?bundle_nss}"
echo "system_nss            %{?system_nss}"
echo "use_rustts            %{?use_rustts}"


%setup -q -n %{tarballdir}
# Build patches, can't change backup suffix from default because during build
# there is a compare of config and js/config directories and .orig suffix is
# ignored during this compare.

%patch4  -p1 -b .build-mozconfig-fix
%patch6  -p1 -b .nss-version

# Fedora patches
%patch215 -p1 -b .addons
%patch219 -p1 -b .rhbz-1173156
%patch224 -p1 -b .1170092

# the nss changed in 8.6 and later, so addons are working in older releases
%if 0%{?rhel_minor_version} >= 6
%patch225 -p1 -b .firefox-nss-addon-hack
%endif

%if 0%{?rhel} >= 9
%patch225 -p1 -b .firefox-nss-addon-hack
%endif

# Patch for big endian platforms only
%if 0%{?big_endian}
%endif

%patch503 -p1 -b .mozilla-s390-context
%patch505 -p1 -b .mozilla-bmo1005535
%patch506 -p1 -b .mozilla-bmo1504834-part1
%patch507 -p1 -b .mozilla-bmo1504834-part2
%patch508 -p1 -b .mozilla-bmo1504834-part3
%patch509 -p1 -b .mozilla-bmo1504834-part4
%patch510 -p1 -b .mozilla-bmo1554971
%patch511 -p1 -b .mozilla-bmo1602730
%patch512 -p1 -b .mozilla-bmo849632
%patch513 -p1 -b .mozilla-bmo998749
#%patch514 -p1 -b .mozilla-s390x-skia-gradient
%patch515 -p1 -b .mozilla-bmo1626236
%patch518 -p1 -b .D110204-fscreen.diff
%patch519 -p1 -b .expat-CVE-2022-25235
%patch520 -p1 -b .expat-CVE-2022-25236
%patch521 -p1 -b .expat-CVE-2022-25315


%patch1001 -p1 -b .ppc64le-inline
%if 0%{?rhel} == 7
# fix the /usr/lib/rpm/debugedit: canonicalization unexpectedly shrank by one character
%patch1009 -p1 -b .build-debuginfo-fix
  %ifarch %{ix86}
# -F dwarf not available in RHEL7's nasm
%patch1008 -p1 -b .build-rhel7-nasm-dwarf
  %endif
%endif

%{__rm} -f .mozconfig
%{__cp} %{SOURCE10} .mozconfig
%if %{official_branding}
echo "ac_add_options --enable-official-branding" >> .mozconfig
%endif
%{__cp} %{SOURCE24} mozilla-api-key
%{__cp} %{SOURCE27} google-api-key

%if %{?system_nss}
echo "ac_add_options --with-system-nspr" >> .mozconfig
echo "ac_add_options --with-system-nss" >> .mozconfig
%else
echo "ac_add_options --without-system-nspr" >> .mozconfig
echo "ac_add_options --without-system-nss" >> .mozconfig
%endif

%ifarch %{ix86} x86_64
echo "ac_add_options --disable-elf-hack" >> .mozconfig
%endif

%if %{?debug_build}
echo "ac_add_options --enable-debug" >> .mozconfig
echo "ac_add_options --disable-optimize" >> .mozconfig
%else
%global optimize_flags "-g -O2"
%ifarch s390x
%global optimize_flags "-g -O2"
%endif
%ifarch ppc64le aarch64
%global optimize_flags "-g -O2"
%endif
%if %{optimize_flags} != "none"
echo 'ac_add_options --enable-optimize=%{?optimize_flags}' >> .mozconfig
%else
echo 'ac_add_options --enable-optimize' >> .mozconfig
%endif
echo "ac_add_options --disable-debug" >> .mozconfig
%endif

# Second arches fail to start with jemalloc enabled
%ifnarch %{ix86} x86_64
echo "ac_add_options --disable-jemalloc" >> .mozconfig
%endif

%ifnarch %{ix86} x86_64
echo "ac_add_options --disable-webrtc" >> .mozconfig
%endif

%if %{?run_tests}
echo "ac_add_options --enable-tests" >> .mozconfig
%endif

%ifarch s390x
echo "ac_add_options --disable-jit" >> .mozconfig
%endif

%ifnarch %{ix86}
%if !0%{?debug_build}
echo "ac_add_options --disable-debug-symbols" >> .mozconfig
%endif
%endif

# AV1 requires newer nasm that was rebased in 8.4
%if 0%{?rhel} == 7 || (0%{?rhel} == 8 && %{rhel_minor_version} < 4)
echo "ac_add_options --disable-av1" >> .mozconfig
%endif

echo 'export NODEJS="%{_buildrootdir}/bin/node-stdout-nonblocking-wrapper"' >> .mozconfig

# Remove executable bit to make brp-mangle-shebangs happy.
chmod -x third_party/rust/itertools/src/lib.rs
chmod a-x third_party/rust/gfx-backend-vulkan/src/*.rs
chmod a-x third_party/rust/gfx-hal/src/*.rs
chmod a-x third_party/rust/ash/src/extensions/ext/*.rs
chmod a-x third_party/rust/ash/src/extensions/khr/*.rs
chmod a-x third_party/rust/ash/src/extensions/mvk/*.rs
chmod a-x third_party/rust/ash/src/extensions/nv/*.rs

#---------------------------------------------------------------------

%build
# Disable LTO to work around rhbz#1883904
%define _lto_cflags %{nil}
ulimit -a
free
#set -e
# Hack for missing shell when building in brew on RHEL6

%if ! 0%{?avoid_bundled_rebuild}
    rm -rf %{_buildrootdir}/*
%endif
export PATH="%{_buildrootdir}/bin:$PATH"

function install_rpms_to_current_dir() {
    PACKAGE_RPM=$(eval echo $1)
    PACKAGE_DIR=%{_rpmdir}

    if [ ! -f $PACKAGE_DIR/$PACKAGE_RPM ]; then
        # Hack for tps tests
        ARCH_STR=%{_arch}
        %ifarch %{ix86}
            ARCH_STR="i?86"
        %endif
        PACKAGE_DIR="$PACKAGE_DIR/$ARCH_STR"
     fi

     for package in $(ls $PACKAGE_DIR/$PACKAGE_RPM)
     do
         echo "$package"
         rpm2cpio "$package" | cpio -idu
     done
}

function build_bundled_package() {
  PACKAGE_RPM=$1
  PACKAGE_FILES=$2
  PACKAGE_SOURCE=$3
  PACKAGE_BUILD_OPTIONS=$4
  export PACKAGE_DIR="%{_topdir}/RPMS"

  PACKAGE_ALREADY_BUILD=0
  %if %{?avoid_bundled_rebuild}
    if ls $PACKAGE_DIR/$PACKAGE_RPM; then
      PACKAGE_ALREADY_BUILD=1
    fi
    if ls $PACKAGE_DIR/%{_arch}/$PACKAGE_RPM; then
      PACKAGE_ALREADY_BUILD=1
    fi
  %endif
  if [ $PACKAGE_ALREADY_BUILD == 0 ]; then
    echo "Rebuilding $PACKAGE_RPM from $PACKAGE_SOURCE"; echo "==============================="
    rpmbuild --nodeps $PACKAGE_BUILD_OPTIONS --rebuild $PACKAGE_SOURCE
    cat /var/tmp/rpm-tmp*
  fi

  find $PACKAGE_DIR
  if [ ! -f $PACKAGE_DIR/$PACKAGE_RPM ]; then
    # Hack for tps tests
    ARCH_STR=%{_arch}
    %ifarch %{ix86}
    ARCH_STR="i?86"
    %endif
    export PACKAGE_DIR="$PACKAGE_DIR/$ARCH_STR"
  fi
  pushd $PACKAGE_DIR

  echo "Installing $PACKAGE_DIR/$PACKAGE_RPM"; echo "==============================="
  pwd
  PACKAGE_LIST=$(echo $PACKAGE_DIR/$PACKAGE_RPM | tr " " "\n")
  for PACKAGE in $PACKAGE_LIST
  do
      rpm2cpio $PACKAGE | cpio -iduv
  done

  PATH=$PACKAGE_DIR/usr/bin:$PATH
  export PATH
  LD_LIBRARY_PATH=$PACKAGE_DIR/usr/%{_lib}:$LD_LIBRARY_PATH
  export LD_LIBRARY_PATH

  # Clean rpms to avoid including them to package
  %if ! 0%{?avoid_bundled_rebuild}
    rm -f $PACKAGE_FILES
  %endif

  popd
}

%if 0%{?bundle_nss}
  rpm -ivh %{SOURCE402}
  #rpmbuild --nodeps --define '_prefix %{bundled_install_path}' --without=tests -ba %{_specdir}/nspr.spec
  rpmbuild --nodeps --define '_prefix %{bundled_install_path}' --without=tests -ba %{_specdir}/nspr.spec
  pushd %{_buildrootdir}
  install_rpms_to_current_dir nspr-4*.rpm
  install_rpms_to_current_dir nspr-devel*.rpm
  popd
  echo "Setting nspr flags"
  # nss-setup-flags-env.inc
  sed -i 's@%{bundled_install_path}@%{_buildrootdir}%{bundled_install_path}@g' %{_buildrootdir}%{bundled_install_path}/%{_lib}/pkgconfig/nspr*.pc

  export LDFLAGS="-L%{_buildrootdir}%{bundled_install_path}/%{_lib} $LDFLAGS"
  export LDFLAGS="-Wl,-rpath,%{bundled_install_path}/%{_lib} $LDFLAGS"
  export LDFLAGS="-Wl,-rpath-link,%{_buildrootdir}%{bundled_install_path}/%{_lib} $LDFLAGS"
  export PKG_CONFIG_PATH=%{_buildrootdir}%{bundled_install_path}/%{_lib}/pkgconfig
  export PATH="{_buildrootdir}%{bundled_install_path}/bin:$PATH"

  export PATH=%{_buildrootdir}/%{bundled_install_path}/bin:$PATH
  echo $PKG_CONFIG_PATH

  rpm -ivh %{SOURCE403}
  rpmbuild --nodeps --define '_prefix %{bundled_install_path}' --without=tests -ba %{_specdir}/nss.spec
  pushd %{_buildrootdir}
  #cleanup
  #rm -rf {_buildrootdir}/usr/lib/debug/*
  #rm -rf {_buildrootdir}/usr/lib/.build-id
  install_rpms_to_current_dir nss-3*.rpm
  install_rpms_to_current_dir nss-devel*.rpm
  install_rpms_to_current_dir nss-pkcs11-devel*.rpm
  install_rpms_to_current_dir nss-softokn-3*.rpm
  install_rpms_to_current_dir nss-softokn-devel*.rpm
  install_rpms_to_current_dir nss-softokn-freebl-3*.rpm
  install_rpms_to_current_dir nss-softokn-freebl-devel*.rpm
  install_rpms_to_current_dir nss-util-3*.rpm
  install_rpms_to_current_dir nss-util-devel*.rpm
  popd
  %filter_provides_in %{bundled_install_path}/%{_lib}
  %filter_requires_in %{bundled_install_path}/%{_lib}
  %filter_from_requires /libnss3.so.*/d
  %filter_from_requires /libsmime3.so.*/d
  %filter_from_requires /libssl3.so.*/d
  %filter_from_requires /libnssutil3.so.*/d
  %filter_from_requires /libnspr4.so.*/d
  find %{_buildrootdir}
%endif

%if 0%{use_bundled_ffi}
  # Install libraries to the predefined location to later add them to the Firefox libraries
  rpm -ivh %{SOURCE303}
  rpmbuild --nodeps --define '_prefix %{bundled_install_path}' -ba %{_specdir}/libffi.spec
  pushd %{_buildrootdir}
  install_rpms_to_current_dir 'libffi*.rpm'
  popd
  %filter_from_requires /libffi.so.6/d
%endif
%filter_setup

function replace_prefix() {
  FILE_NAME=$1
  PKG_CONFIG_PREFIX=$2

  cat $FILE_NAME | tail -n +2 > tmp.txt
  echo "$PKG_CONFIG_PREFIX" > $FILE_NAME
  cat tmp.txt >> $FILE_NAME
  rm -rf tmp.txt
}

# We need to disable exit on error temporarily for the following scripts:
set +e
%if 0%{?use_dts}
source scl_source enable devtoolset-%{dts_version}
%endif
%if 0%{?use_rustts}
source scl_source enable rust-toolset-%{rust_version}
%endif
%if 0%{?use_nodejsts}
source scl_source enable rh-nodejs10
%endif

env
which gcc
which c++
which g++
which ld
which nasm
# Build and install local node if needed
# ======================================
export MOZ_NODEJS=`which node`

mkdir -p my_rust_vendor
cd my_rust_vendor
%{__tar} xf %{SOURCE2}
cd -
mkdir -p .cargo
cat > .cargo/config <<EOL
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "`pwd`/my_rust_vendor"
EOL

export CARGO_HOME=.cargo
cargo install cbindgen
export PATH=`pwd`/.cargo/bin:$PATH
export CBINDGEN=`pwd`/.cargo/bin/cbindgen

# debug missing sqlite3 python module
export MACH_USE_SYSTEM_PYTHON=1
./mach python -c "import sys;print(sys.path)"

mkdir %{_buildrootdir}/bin || :
cp %{SOURCE28} %{_buildrootdir}/bin || :
chmod +x %{_buildrootdir}/bin/node-stdout-nonblocking-wrapper

# Update the various config.guess to upstream release for aarch64 support
find ./ -name config.guess -exec cp /usr/lib/rpm/config.guess {} ';'

# -fpermissive is needed to build with gcc 4.6+ which has become stricter
#
# Mozilla builds with -Wall with exception of a few warnings which show up
# everywhere in the code; so, don't override that.
#
# Disable C++ exceptions since Mozilla code is not exception-safe
#
MOZ_OPT_FLAGS=$(echo "%{optflags}" | %{__sed} -e 's/-Wall//')
#rhbz#1037063
# -Werror=format-security causes build failures when -Wno-format is explicitly given
# for some sources
# Explicitly force the hardening flags for Firefox so it passes the checksec test;
# See also https://fedoraproject.org/wiki/Changes/Harden_All_Packages
MOZ_OPT_FLAGS="$MOZ_OPT_FLAGS -Wformat-security -Wformat -Werror=format-security"

%if %{?hardened_build}
  MOZ_OPT_FLAGS="$MOZ_OPT_FLAGS -fPIC -Wl,-z,relro -Wl,-z,now"
  %endif
%if %{?debug_build}
  MOZ_OPT_FLAGS=$(echo "$MOZ_OPT_FLAGS" | %{__sed} -e 's/-O2//')
%endif

# We don't wantfirefox to use CK_GCM_PARAMS_V3 in nss
MOZ_OPT_FLAGS="$MOZ_OPT_FLAGS -DNSS_PKCS11_3_0_STRICT"

%if !%{build_with_clang}
  %ifarch aarch64 %{ix86} x86_64 s390x
    MOZ_LINK_FLAGS="-Wl,--no-keep-memory -Wl,--reduce-memory-overheads"
  %endif
  %ifarch %{ix86}
    MOZ_LINK_FLAGS="-Wl,--no-keep-memory -Wl,--strip-debug"
    echo "ac_add_options --enable-linker=gold" >> .mozconfig
  %endif
%endif

%if 0%{?bundle_nss}
  mkdir -p %{_buildrootdir}%{bundled_install_path}/%{_lib}
  MOZ_LINK_FLAGS="-L%{_buildrootdir}%{bundled_install_path}/%{_lib} $MOZ_LINK_FLAGS"
  MOZ_LINK_FLAGS="-Wl,-rpath,%{bundled_install_path}/%{_lib} $MOZ_LINK_FLAGS"
  MOZ_LINK_FLAGS="-Wl,-rpath-link,%{_buildrootdir}%{bundled_install_path}/%{_lib} $MOZ_LINK_FLAGS"
%endif

%ifarch %{ix86}
  export RUSTFLAGS="-Cdebuginfo=0"
  echo 'export RUSTFLAGS="-Cdebuginfo=0"' >> .mozconfig
%endif

export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'
export CC=gcc
export CXX=g++
echo "export CFLAGS=\"$MOZ_OPT_FLAGS\"" >> .mozconfig
echo "export CXXFLAGS=\"$MOZ_OPT_FLAGS\"" >> .mozconfig
echo "export LDFLAGS=\"$MOZ_LINK_FLAGS\"" >> .mozconfig

%if %{build_with_clang}
  echo "export LLVM_PROFDATA=\"llvm-profdata\"" >> .mozconfig
  echo "export AR=\"llvm-ar\"" >> .mozconfig
  echo "export NM=\"llvm-nm\"" >> .mozconfig
  echo "export RANLIB=\"llvm-ranlib\"" >> .mozconfig
  echo "ac_add_options --enable-linker=lld" >> .mozconfig
%else
  echo "export CC=gcc" >> .mozconfig
  echo "export CXX=g++" >> .mozconfig
  echo "export AR=\"gcc-ar\"" >> .mozconfig
  echo "export NM=\"gcc-nm\"" >> .mozconfig
  echo "export RANLIB=\"gcc-ranlib\"" >> .mozconfig
%endif

MOZ_SMP_FLAGS=-j1
# More than two build tasks can lead to OOM gcc crash.
%if 0%{?rhel} < 8
  [ -z "$RPM_BUILD_NCPUS" ] && \
       RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"
  [ "$RPM_BUILD_NCPUS" -ge 2 ] && MOZ_SMP_FLAGS=-j2
%else
  %ifarch %{ix86} x86_64 ppc64 ppc64le aarch64
  [ -z "$RPM_BUILD_NCPUS" ] && \
       RPM_BUILD_NCPUS="`/usr/bin/getconf _NPROCESSORS_ONLN`"
    [ "$RPM_BUILD_NCPUS" -ge 2 ] && MOZ_SMP_FLAGS=-j2
    [ "$RPM_BUILD_NCPUS" -ge 4 ] && MOZ_SMP_FLAGS=-j3
    [ "$RPM_BUILD_NCPUS" -ge 8 ] && MOZ_SMP_FLAGS=-j3
  %endif
%endif

cat /proc/meminfo

# Free memory in kB
if grep -q MemAvailable /proc/meminfo; then
    MEM_AVAILABLE=$(grep MemAvailable /proc/meminfo | awk '{ print $2 }')
else
    MEM_AVAILABLE=$(grep MemFree /proc/meminfo | awk '{ print $2 }')
fi

# Usually the compiler processes can take 2 GB of memory at peaks
TASK_SIZE=4000000
MEM_CONSTRAINED_JOBS=$(( MEM_AVAILABLE / TASK_SIZE ))

if [ $MEM_CONSTRAINED_JOBS -le 0 ]; then
  MEM_CONSTRAINED_JOBS=1
fi

CPU_AVAILABLE=$(/usr/bin/getconf _NPROCESSORS_ONLN)
# Pick the minimum from available CPUs or memory constrained number of jobs
MOZ_SMP_FLAGS=-j$([ "$CPU_AVAILABLE" -le "$MEM_CONSTRAINED_JOBS" ] && echo "$CPU_AVAILABLE" || echo "$MEM_CONSTRAINED_JOBS")

# override smp flags to the rpmbuild defaults ATM
%ifnarch ppc64le
MOZ_SMP_FLAGS=%{_smp_mflags}
%endif

%ifarch s390x
MOZ_SMP_FLAGS=-j2
%endif

%if 0%{?bundle_nss}
  echo "Setting nss flags"
  # nss-setup-flags-env.inc
  %include_file %{SOURCE401}
  export PATH=%{_buildrootdir}/%{bundled_install_path}/bin:$PATH
  echo $PKG_CONFIG_PATH
%endif

export MOZ_MAKE_FLAGS="$MOZ_SMP_FLAGS"
export MOZ_SERVICES_SYNC="1"
# we need to strip the sources on i686 because to we don't use rpm to generate debugsymbols because of oom
%ifnarch %{ix86}
  export STRIP=/bin/true
%endif
which node
echo 'export NODEJS="%{_buildrootdir}/bin/node-stdout-nonblocking-wrapper"'
env
ls %{_buildrootdir}

export MACH_USE_SYSTEM_PYTHON=1
%if 0%{?use_llvmts}
  #scl enable llvm-toolset-%{llvm_version} './mach build -v'
  ./mach build -v || exit 1
%else
  ./mach build -v || exit 1
%endif
# Look for the reason we get: /usr/lib/rpm/debugedit: canonicalization unexpectedly shrank by one character
readelf -wl objdir/dist/bin/libxul.so | grep "/"

%if %{?run_tests}
  %if %{?system_nss}
    ln -s /usr/bin/certutil objdir/dist/bin/certutil
    ln -s /usr/bin/pk12util objdir/dist/bin/pk12util
  %endif
  mkdir test_results
  ./mach --log-no-times check-spidermonkey &> test_results/check-spidermonkey || true
  ./mach --log-no-times check-spidermonkey &> test_results/check-spidermonkey-2nd-run || true
  ./mach --log-no-times cppunittest &> test_results/cppunittest || true
  xvfb-run ./mach --log-no-times crashtest &> test_results/crashtest || true
  ./mach --log-no-times gtest &> test_results/gtest || true
  xvfb-run ./mach --log-no-times jetpack-test &> test_results/jetpack-test || true
  # not working right now ./mach marionette-test &> test_results/marionette-test || true
  xvfb-run ./mach --log-no-times mochitest-a11y &> test_results/mochitest-a11y || true
  xvfb-run ./mach --log-no-times mochitest-browser &> test_results/mochitest-browser || true
  xvfb-run ./mach --log-no-times mochitest-chrome &> test_results/mochitest-chrome || true
  xvfb-run ./mach --log-no-times mochitest-devtools &> test_results/mochitest-devtools || true
  xvfb-run ./mach --log-no-times mochitest-plain &> test_results/mochitest-plain || true
  xvfb-run ./mach --log-no-times reftest &> test_results/reftest || true
  xvfb-run ./mach --log-no-times webapprt-test-chrome &> test_results/webapprt-test-chrome || true
  xvfb-run ./mach --log-no-times webapprt-test-content &> test_results/webapprt-test-content || true
  ./mach --log-no-times webidl-parser-test &> test_results/webidl-parser-test || true
  xvfb-run ./mach --log-no-times xpcshell-test &> test_results/xpcshell-test || true
  %if %{?system_nss}
    rm -f  objdir/dist/bin/certutil
    rm -f  objdir/dist/bin/pk12util
  %endif
%endif
#---------------------------------------------------------------------

%install
export MACH_USE_SYSTEM_PYTHON=1
function install_rpms_to_current_dir() {
    PACKAGE_RPM=$(eval echo $1)
    PACKAGE_DIR=%{_rpmdir}

    if [ ! -f $PACKAGE_DIR/$PACKAGE_RPM ]; then
        # Hack for tps tests
        ARCH_STR=%{_arch}
        %ifarch %{ix86}
            ARCH_STR="i?86"
        %endif
        PACKAGE_DIR="$PACKAGE_DIR/$ARCH_STR"
     fi

     for package in $(ls $PACKAGE_DIR/$PACKAGE_RPM)
     do
         echo "$package"
         rpm2cpio "$package" | cpio -idu
     done
}

%if 0%{?bundle_nss}
  pushd %{buildroot}
  #install_rpms_to_current_dir nss-*.rpm
  install_rpms_to_current_dir nspr-4*.rpm
  install_rpms_to_current_dir nss-3*.rpm
  install_rpms_to_current_dir nss-softokn-3*.rpm
  install_rpms_to_current_dir nss-softokn-freebl-3*.rpm
  install_rpms_to_current_dir nss-util-3*.rpm

  # cleanup unecessary nss files
  #rm -rf %{_buildrootdir}/%{bundled_install_path}/bin
  #rm -rf %{_buildrootdir}/%{bundled_install_path}/include
  rm -rf %{buildroot}/%{bundled_install_path}/lib/dracut
  rm -rf %{buildroot}/%{bundled_install_path}/%{_lib}/nss
  #rm -rf %{_buildrootdir}/%{bundled_install_path}/%{_lib}/pkgconfig
  rm -rf %{buildroot}/%{bundled_install_path}/%{_lib}/share
  rm -rf %{buildroot}/%{bundled_install_path}/share
  rm -rf %{buildroot}/etc/pki
  rm -rf %{buildroot}/usr/lib/.build-id
  rm -rf %{buildroot}/etc/crypto-policies
  popd
%endif

# Install bundled libffi
%if %{use_bundled_ffi}
  pushd %{buildroot}
  install_rpms_to_current_dir libffi-3*.rpm
  popd
%endif

# set up our default bookmarks
%{__cp} -p %{default_bookmarks_file} objdir/dist/bin/browser/chrome/en-US/locale/browser/bookmarks.html

# Make sure locale works for langpacks
%{__cat} > objdir/dist/bin/browser/defaults/preferences/firefox-l10n.js << EOF
pref("general.useragent.locale", "chrome://global/locale/intl.properties");
EOF

DESTDIR=%{buildroot} make -C objdir install

%{__mkdir_p} %{buildroot}{%{_libdir},%{_bindir},%{_datadir}/applications}

desktop-file-install --dir %{buildroot}%{_datadir}/applications %{SOURCE20}

# set up the firefox start script
%{__rm} -rf %{buildroot}%{_bindir}/firefox
%{__cat} %{SOURCE21} > %{buildroot}%{_bindir}/firefox
sed -i -e 's|%PREFIX%|%{_prefix}|' %{buildroot}%{_bindir}/firefox
sed -i -e 's|%RHEL_ENV_VARS%||' %{buildroot}%{_bindir}/firefox

%{__chmod} 755 %{buildroot}%{_bindir}/firefox

%{__install} -p -D -m 644 %{SOURCE23} %{buildroot}%{_mandir}/man1/firefox.1

%{__rm} -f %{buildroot}/%{mozappdir}/firefox-config
%{__rm} -f %{buildroot}/%{mozappdir}/update-settings.ini

for s in 16 22 24 32 48 256; do
    %{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps
    %{__cp} -p browser/branding/official/default${s}.png \
               %{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps/firefox.png
done

# Install hight contrast icon
%{__mkdir_p} %{buildroot}%{_datadir}/icons/hicolor/symbolic/apps
%{__cp} -p %{SOURCE25} \
           %{buildroot}%{_datadir}/icons/hicolor/symbolic/apps

# Register as an application to be visible in the software center
#
# NOTE: It would be *awesome* if this file was maintained by the upstream
# project, translated and installed into the right place during `make install`.
#
# See http://www.freedesktop.org/software/appstream/docs/ for more details.
#
%{__mkdir_p} %{buildroot}%{_datadir}/appdata
cat > %{buildroot}%{_datadir}/appdata/%{name}.appdata.xml <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!-- Copyright 2014 Richard Hughes <richard@hughsie.com> -->
<!--
BugReportURL: https://bugzilla.mozilla.org/show_bug.cgi?id=1071061
SentUpstream: 2014-09-22
-->
<application>
  <id type="desktop">firefox.desktop</id>
  <metadata_license>CC0-1.0</metadata_license>
  <project_license>MPLv1.1 or GPLv2+ or LGPLv2+</project_license>
  <description>
    <p>
      Bringing together all kinds of awesomeness to make browsing better for you.
      Get to your favorite sites quickly – even if you don’t remember the URLs.
      Type your term into the location bar (aka the Awesome Bar) and the autocomplete
      function will include possible matches from your browsing history, bookmarked
      sites and open tabs.
    </p>
    <!-- FIXME: Needs another couple of paragraphs -->
  </description>
  <url type="homepage">http://www.mozilla.org/</url>
  <screenshots>
    <screenshot type="default">https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/firefox/a.png</screenshot>
    <screenshot>https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/firefox/b.png</screenshot>
    <screenshot>https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/firefox/c.png</screenshot>
  </screenshots>
  <!-- FIXME: change this to an upstream email address for spec updates
  <updatecontact>someone_who_cares@upstream_project.org</updatecontact>
   -->
</application>
EOF

echo > %{name}.lang
%if %{build_langpacks}
# Extract langpacks, make any mods needed, repack the langpack, and install it.
%{__mkdir_p} %{buildroot}%{langpackdir}
%{__tar} xf %{SOURCE1}
for langpack in `ls firefox-langpacks/*.xpi`; do
  language=`basename $langpack .xpi`
  extensionID=langpack-$language@firefox.mozilla.org
  %{__mkdir_p} $extensionID
  unzip -qq $langpack -d $extensionID
  find $extensionID -type f | xargs chmod 644

  cd $extensionID
  zip -qq -r9mX ../${extensionID}.xpi *
  cd -

  %{__install} -m 644 ${extensionID}.xpi %{buildroot}%{langpackdir}
  language=`echo $language | sed -e 's/-/_/g'`
  echo "%%lang($language) %{langpackdir}/${extensionID}.xpi" >> %{name}.lang
done
%{__rm} -rf firefox-langpacks

# Install langpack workaround (see #707100, #821169)
function create_default_langpack() {
language_long=$1
language_short=$2
cd %{buildroot}%{langpackdir}
ln -s langpack-$language_long@firefox.mozilla.org.xpi langpack-$language_short@firefox.mozilla.org.xpi
cd -
echo "%%lang($language_short) %{langpackdir}/langpack-$language_short@firefox.mozilla.org.xpi" >> %{name}.lang
}

# Table of fallbacks for each language
# please file a bug at bugzilla.redhat.com if the assignment is incorrect
create_default_langpack "es-AR" "es"
create_default_langpack "fy-NL" "fy"
create_default_langpack "ga-IE" "ga"
create_default_langpack "gu-IN" "gu"
create_default_langpack "hi-IN" "hi"
create_default_langpack "hy-AM" "hy"
create_default_langpack "nb-NO" "nb"
create_default_langpack "nn-NO" "nn"
create_default_langpack "pa-IN" "pa"
create_default_langpack "pt-PT" "pt"
create_default_langpack "sv-SE" "sv"
create_default_langpack "zh-TW" "zh"
%endif

# Keep compatibility with the old preference location.
%{__mkdir_p} %{buildroot}%{mozappdir}/defaults/preferences
%{__mkdir_p} %{buildroot}%{mozappdir}/browser/defaults
ln -s %{mozappdir}/defaults/preferences $RPM_BUILD_ROOT/%{mozappdir}/browser/defaults/preferences
# Default preferences
%{__cp} %{SOURCE12} %{buildroot}%{mozappdir}/defaults/preferences/all-redhat.js
sed -i -e 's|%PREFIX%|%{_prefix}|' %{buildroot}%{mozappdir}/defaults/preferences/all-redhat.js
# Enable modern crypto for the key export on the RHEL9 only (rhbz#1764205)
%if 0%{?rhel} == 9
  echo 'pref("security.pki.use_modern_crypto_with_pkcs12", true);' >> %{buildroot}%{mozappdir}/defaults/preferences/all-redhat.js
%endif

%ifarch s390x
  echo 'pref("gfx.webrender.force-disabled", true);' >> %{buildroot}%{mozappdir}/defaults/preferences/all-redhat.js
%endif


# System config dir
%{__mkdir_p} %{buildroot}/%{_sysconfdir}/%{name}/pref

# System extensions
%{__mkdir_p} %{buildroot}%{_datadir}/mozilla/extensions/%{firefox_app_id}
%{__mkdir_p} %{buildroot}%{_libdir}/mozilla/extensions/%{firefox_app_id}

# Copy over the LICENSE
%{__install} -p -c -m 644 LICENSE %{buildroot}/%{mozappdir}

# Use the system hunspell dictionaries
%{__rm} -rf %{buildroot}%{mozappdir}/dictionaries
ln -s %{_datadir}/myspell %{buildroot}%{mozappdir}/dictionaries

%if %{run_tests}
# Add debuginfo for crash-stats.mozilla.com
%{__mkdir_p} %{buildroot}/test_results
%{__cp} test_results/* %{buildroot}/test_results
%endif


# Copy over run-mozilla.sh
%{__cp} build/unix/run-mozilla.sh %{buildroot}%{mozappdir}

# Add distribution.ini
%{__mkdir_p} %{buildroot}%{mozappdir}/distribution
%{__cp} %{SOURCE26} %{buildroot}%{mozappdir}/distribution

%if 0%{?centos}
sed -i -e 's|Red Hat Enterprise|CentOS|' %{buildroot}%{mozappdir}/distribution/distribution.ini
%endif

# Remove copied libraries to speed up build
rm -f %{buildroot}%{mozappdirdev}/sdk/lib/libmozjs.so
rm -f %{buildroot}%{mozappdirdev}/sdk/lib/libmozalloc.so
rm -f %{buildroot}%{mozappdirdev}/sdk/lib/libxul.so
#---------------------------------------------------------------------

%preun
# is it a final removal?
if [ $1 -eq 0 ]; then
  %{__rm} -rf %{mozappdir}/components
  %{__rm} -rf %{mozappdir}/extensions
  %{__rm} -rf %{mozappdir}/plugins
fi

%clean
rm -rf %{_srcrpmdir}/libffi*.src.rpm
find %{_rpmdir} -name "libffi*.rpm" -delete
rm -rf %{_srcrpmdir}/openssl*.src.rpm
find %{_rpmdir} -name "openssl*.rpm" -delete
rm -rf %{_srcrpmdir}/nss*.src.rpm
find %{_rpmdir} -name "nss*.rpm" -delete
rm -rf %{_srcrpmdir}/nspr*.src.rpm
find %{_rpmdir} -name "nspr*.rpm" -delete

%post
update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :

%files -f %{name}.lang
%{_bindir}/firefox
%{mozappdir}/firefox
%{mozappdir}/firefox-bin
%doc %{_mandir}/man1/*
%dir %{_sysconfdir}/%{name}
%dir %{_sysconfdir}/%{name}/*
%dir %{_datadir}/mozilla/extensions/*
%dir %{_libdir}/mozilla/extensions/*
%{_datadir}/appdata/*.appdata.xml
%{_datadir}/applications/*.desktop
%dir %{mozappdir}
%doc %{mozappdir}/LICENSE
%{mozappdir}/browser/chrome
%{mozappdir}/defaults/preferences/*
%{mozappdir}/browser/defaults/preferences
%{mozappdir}/browser/features/*.xpi
%{mozappdir}/distribution/distribution.ini
%if %{build_langpacks}
%dir %{langpackdir}
%endif
%{mozappdir}/browser/omni.ja
%{mozappdir}/run-mozilla.sh
%{mozappdir}/application.ini
%{mozappdir}/pingsender
%exclude %{mozappdir}/removed-files
%{_datadir}/icons/hicolor/16x16/apps/firefox.png
%{_datadir}/icons/hicolor/22x22/apps/firefox.png
%{_datadir}/icons/hicolor/24x24/apps/firefox.png
%{_datadir}/icons/hicolor/256x256/apps/firefox.png
%{_datadir}/icons/hicolor/32x32/apps/firefox.png
%{_datadir}/icons/hicolor/48x48/apps/firefox.png
%{_datadir}/icons/hicolor/symbolic/apps/firefox-symbolic.svg
%{mozappdir}/*.so
%{mozappdir}/defaults/pref/channel-prefs.js
%{mozappdir}/dependentlibs.list
%{mozappdir}/dictionaries
%{mozappdir}/omni.ja
%{mozappdir}/platform.ini
%{mozappdir}/plugin-container
%{mozappdir}/gmp-clearkey
%{mozappdir}/fonts/*.ttf
%if !%{?system_nss}
%exclude %{mozappdir}/libnssckbi.so
%endif
%if 0%{use_bundled_ffi}
%{mozappdir}/bundled/%{_lib}/libffi.so*
%exclude %{_datadir}/doc/libffi*
%endif

%if 0%{?bundle_nss}
%{mozappdir}/bundled/%{_lib}/libfreebl*
%{mozappdir}/bundled/%{_lib}/libnss3*
%{mozappdir}/bundled/%{_lib}/libnssdbm3*
%{mozappdir}/bundled/%{_lib}/libnssutil3*
%{mozappdir}/bundled/%{_lib}/libsmime3*
%{mozappdir}/bundled/%{_lib}/libsoftokn*
%{mozappdir}/bundled/%{_lib}/libssl3*
%{mozappdir}/bundled/%{_lib}/libnspr4.so
%{mozappdir}/bundled/%{_lib}/libplc4.so
%{mozappdir}/bundled/%{_lib}/libplds4.so
%endif


#---------------------------------------------------------------------

%changelog
* Tue May 17 2022 CentOS Sources <bugs@centos.org> - 91.8.0-1.el9.centos
- Apply debranding changes

* Tue Apr 05 2022 Eike Rathke <erack@redhat.com> - 91.8.0-1
- Update to 91.8.0

* Mon Mar 07 2022 Eike Rathke <erack@redhat.com> - 91.7.0-3
- Update to 91.7.0 build3

* Wed Mar 02 2022 Jan Horak <jhorak@redhat.com> - 91.7.0-2
- Added expat backports of CVE-2022-25235, CVE-2022-25236 and CVE-2022-25315

* Tue Mar 01 2022 Eike Rathke <erack@redhat.com> - 91.7.0-1
- Update to 91.7.0 build2

* Wed Feb 09 2022 Jan Horak <jhorak@redhat.com> - 91.6.0-2
- Enable addon installation on rhel9

* Wed Feb 02 2022 Eike Rathke <erack@redhat.com> - 91.6.0-1
- Update to 91.6.0 build1

* Wed Feb 02 2022 Jan Horak <jhorak@redhat.com> - 91.5.0-2
- Use default update channel to fix non working enterprise policies:
  rhbz#2044667

* Thu Jan 06 2022 Eike Rathke <erack@redhat.com> - 91.5.0-1
- Update to 91.5.0 build1

* Wed Dec 22 2021 Jan Horak <jhorak@redhat.com> - 91.4.0-3
- Enable optimalization on s390x

* Mon Dec 13 2021 Jan Horak <jhorak@redhat.com> - 91.4.0-2
- Added fix for failing addons signatures.

* Wed Dec 01 2021 Eike Rathke <erack@redhat.com> - 91.4.0-1
- Update to 91.4.0 build1

* Mon Nov 01 2021 Eike Rathke <erack@redhat.com> - 91.3.0-1
- Update to 91.3.0 build1

* Thu Oct 21 2021 Jan Horak <jhorak@redhat.com> - 91.2.0-5
- Fixed crashes when FIPS is enabled.

* Mon Oct 04 2021 Jan Horak <jhorak@redhat.com> - 91.2.0-4
- Disable webrender on the s390x due to wrong colors: rhbz#2009503
- Update to 91.2: rhbz#2009145
- Modern algorithms in PKCS#12: rhbz#1764205

* Wed Sep 29 2021 Jan Horak <jhorak@redhat.com> - 91.2.0-3
- Update to 91.2.0 build1

* Wed Sep 15 2021 Jan Horak <jhorak@redhat.com> - 91.1.0-1
- Update to 91.1.0 build1

* Tue Aug 17 2021 Jan Horak <jhorak@redhat.com>
- Update to 91.0.1 build1

* Tue Aug 10 2021 Jan Horak <jhorak@redhat.com> - 91.0-1
- Update to 91.0 ESR

* Thu Jul 29 2021 Jan Horak <jhorak@redhat.com> - 91.0-1
- Update to 91.0b8

* Fri Jul 16 2021 Jan Horak <jhorak@redhat.com> - 78.12.0-2
- Rebuild to pickup older nss

* Wed Jul 07 2021 Eike Rathke <erack@redhat.com> - 78.12.0-1
- Update to 78.12.0 build1

* Mon May 31 2021 Eike Rathke <erack@redhat.com> - 78.11.0-3
- Update to 78.11.0 build2 (release)

* Thu May 27 2021 Eike Rathke <erack@redhat.com> - 78.11.0-2
- Fix rhel_minor_version for dist .el8_4 and .el8

* Tue May 25 2021 Eike Rathke <erack@redhat.com> - 78.11.0-1
- Update to 78.11.0 build1

* Tue Apr 20 2021 Eike Rathke <erack@redhat.com> - 78.10.0-1
- Update to 78.10.0

* Wed Mar 17 2021 Eike Rathke <erack@redhat.com> - 78.9.0-1
- Update to 78.9.0 build1

* Wed Feb 17 2021 Eike Rathke <erack@redhat.com> - 78.8.0-1
- Update to 78.8.0 build2

* Tue Feb 09 2021 Eike Rathke <erack@redhat.com> - 78.7.1-1
- Update to 78.7.1

* Tue Feb 09 2021 Jan Horak <jhorak@redhat.com> - 78.7.0-3
- Fixing install prefix for the homepage

* Fri Jan 22 2021 Eike Rathke <erack@redhat.com> - 78.7.0-2
- Update to 78.7.0 build2

* Wed Jan 20 2021 Eike Rathke <erack@redhat.com> - 78.7.0-1
- Update to 78.7.0 build1

* Wed Jan  6 2021 Eike Rathke <erack@redhat.com> - 78.6.1-1
- Update to 78.6.1 build1

* Thu Dec 10 2020 Jan Horak <jhorak@redhat.com> - 78.6.0-1
- Update to 78.6.0 build1

* Wed Nov 18 2020 Jan Horak <jhorak@redhat.com> - 78.5.0-1
- Update to 78.5.0 build1

* Tue Nov 10 2020 erack@redhat.com - 78.4.1-1
- Update to 78.4.1

* Tue Nov 10 2020 Jan Horak <jhorak@redhat.com> - 78.4.0-3
- Fixing flatpak build, fixing firefox.sh.in to not disable langpacks loading

* Thu Oct 29 2020 Jan Horak <jhorak@redhat.com> - 78.4.0-2
- Enable addon sideloading

* Fri Oct 16 2020 Jan Horak <jhorak@redhat.com> - 78.4.0-1
- Update to 78.4.0 build2

* Fri Sep 18 2020 Jan Horak <jhorak@redhat.com>
- Update to 78.3.0 build1

* Tue Aug 18 2020 Jan Horak <jhorak@redhat.com> - 78.2.0-3
- Update to 78.2.0 build1

* Fri Jul 24 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.11.0 build1

* Fri Jun 26 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.10.0 build1

* Fri May 29 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.9.0 build1
- Added patch for pipewire 0.3

* Mon May 11 2020 Jan Horak <jhorak@redhat.com>
- Added s390x specific patches

* Wed Apr 29 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.8.0 build1

* Thu Apr 23 2020 Martin Stransky <stransky@redhat.com> - 68.7.0-3
- Added fix for rhbz#1821418

* Tue Apr 07 2020 Jan Horak <jhorak@redhat.com> - 68.7.0-2
- Update to 68.7.0 build3

* Mon Apr  6 2020 Jan Horak <jhorak@redhat.com> - 68.6.1-1
- Update to 68.6.1 ESR

* Wed Mar 04 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.6.0 build1

* Mon Feb 24 2020 Martin Stransky <stransky@redhat.com> - 68.5.0-3
- Added fix for rhbz#1805667
- Enabled mzbz@1170092 - Firefox prefs at /etc

* Fri Feb 07 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.5.0 build2

* Wed Feb 05 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.5.0 build1

* Wed Jan 08 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.4.1esr build1

* Fri Jan 03 2020 Jan Horak <jhorak@redhat.com>
- Update to 68.4.0esr build1

* Wed Dec 18 2019 Jan Horak <jhorak@redhat.com>
- Fix for wrong intl.accept_lang when using non en-us langpack

* Wed Nov 27 2019 Martin Stransky <stransky@redhat.com> - 68.3.0-1
- Update to 68.3.0 ESR

* Thu Oct 24 2019 Martin Stransky <stransky@redhat.com> - 68.2.0-4
- Added patch for TLS 1.3 support.

* Wed Oct 23 2019 Martin Stransky <stransky@redhat.com> - 68.2.0-3
- Rebuild

* Mon Oct 21 2019 Martin Stransky <stransky@redhat.com> - 68.2.0-2
- Rebuild

* Thu Oct 17 2019 Martin Stransky <stransky@redhat.com> - 68.2.0-1
- Update to 68.2.0 ESR

* Thu Oct 10 2019 Martin Stransky <stransky@redhat.com> - 68.1.0-6
- Enable system nss on RHEL6

* Thu Sep  5 2019 Jan Horak <jhorak@redhat.com> - 68.1.0-2
- Enable building langpacks

* Wed Aug 28 2019 Jan Horak <jhorak@redhat.com> - 68.1.0-1
- Update to 68.1.0 ESR

* Mon Aug 5 2019 Martin Stransky <stransky@redhat.com> - 68.0.1-4
- Enable system nss

* Mon Jul 29 2019 Martin Stransky <stransky@redhat.com> - 68.0.1-3
- Enable official branding

* Fri Jul 26 2019 Martin Stransky <stransky@redhat.com> - 68.0.1-2
- Enabled PipeWire on RHEL8

* Fri Jul 26 2019 Martin Stransky <stransky@redhat.com> - 68.0.1-1
- Updated to 68.0.1 ESR

* Tue Jul 16 2019 Jan Horak <jhorak@redhat.com> - 68.0-0.11
- Update to 68.0 ESR

* Tue Jun 25 2019 Martin Stransky <stransky@redhat.com> - 68.0-0.10
- Updated to 68.0 alpha 13
- Enabled second arches

* Fri Mar 22 2019 Martin Stransky <stransky@redhat.com> - 68.0-0.1
- Updated to 68.0 alpha

* Fri Mar 15 2019 Martin Stransky <stransky@redhat.com> - 60.6.0-3
- Added Google API keys (mozbz#1531176)

* Thu Mar 14 2019 Martin Stransky <stransky@redhat.com> - 60.6.0-2
- Update to 60.6.0 ESR (Build 2)

* Wed Mar 13 2019 Martin Stransky <stransky@redhat.com> - 60.6.0-1
- Update to 60.6.0 ESR (Build 1)

* Wed Feb 13 2019 Jan Horak <jhorak@redhat.com> - 60.5.1-1
- Update to 60.5.1 ESR

* Wed Feb 6 2019 Martin Stransky <stransky@redhat.com> - 60.5.0-3
- Added fix for rhbz#1672424 - Firefox crashes on NFS drives.

* Fri Jan 25 2019 Martin Stransky <stransky@redhat.com> - 60.5.0-2
- Updated to 60.5.0 ESR build2

* Tue Jan 22 2019 Martin Stransky <stransky@redhat.com> - 60.5.0-1
- Updated to 60.5.0 ESR build1

* Thu Jan 10 2019 Jan Horak <jhorak@redhat.com> - 60.4.0-3
- Fixing fontconfig warnings (rhbz#1601475)

* Wed Jan  9 2019 Jan Horak <jhorak@redhat.com> - 60.4.0-2
- Added pipewire patch from Tomas Popela (rhbz#1664270)

* Wed Dec  5 2018 Jan Horak <jhorak@redhat.com> - 60.4.0-1
- Update to 60.4.0 ESR

* Tue Dec  4 2018 Jan Horak <jhorak@redhat.com> - 60.3.0-2
- Added firefox-gnome-shell-extension

* Fri Oct 19 2018 Jan Horak <jhorak@redhat.com> - 60.3.0-1
- Update to 60.3.0 ESR

* Wed Oct 10 2018 Jan Horak <jhorak@redhat.com> - 60.2.2-2
- Added patch for rhbz#1633932

* Tue Oct  2 2018 Jan Horak <jhorak@redhat.com> - 60.2.2-1
- Update to 60.2.2 ESR

* Mon Sep 24 2018 Jan Horak <jhorak@redhat.com> - 60.2.1-1
- Update to 60.2.1 ESR

* Fri Aug 31 2018 Jan Horak <jhorak@redhat.com> - 60.2.0-1
- Update to 60.2.0 ESR

* Tue Aug 28 2018 Jan Horak <jhorak@redhat.com> - 60.1.0-9
- Do not set user agent (rhbz#1608065)
- GTK dialogs are localized now (rhbz#1619373)
- JNLP association works again (rhbz#1607457)

* Thu Aug 16 2018 Jan Horak <jhorak@redhat.com> - 60.1.0-8
- Fixed homepage and bookmarks (rhbz#1606778)
- Fixed missing file associations in RHEL6 (rhbz#1613565)

* Thu Jul 12 2018 Jan Horak <jhorak@redhat.com> - 60.1.0-7
- Run at-spi-bus if not running already (for the bundled gtk3)

* Mon Jul  9 2018 Jan Horak <jhorak@redhat.com> - 60.1.0-6
- Fix for missing schemes for bundled gtk3

* Mon Jun 25 2018 Martin Stransky <stransky@redhat.com> - 60.1.0-5
- Added mesa-libEGL dependency to gtk3/rhel6

* Sun Jun 24 2018 Martin Stransky <stransky@redhat.com> - 60.1.0-4
- Disabled jemalloc on all second arches

* Fri Jun 22 2018 Martin Stransky <stransky@redhat.com> - 60.1.0-3
- Updated to 60.1.0 ESR build2

* Thu Jun 21 2018 Martin Stransky <stransky@redhat.com> - 60.1.0-2
- Disabled jemalloc on second arches

* Wed Jun 20 2018 Martin Stransky <stransky@redhat.com> - 60.1.0-1
- Updated to 60.1.0 ESR

* Wed Jun 13 2018 Jan Horak <jhorak@redhat.com> - 60.0-12
- Fixing bundled libffi issues
- Readded some requirements

* Mon Jun 11 2018 Martin Stransky <stransky@redhat.com> - 60.0-10
- Added fix for mozilla BZ#1436242 - IPC crashes.

* Mon Jun 11 2018 Jan Horak <jhorak@redhat.com> - 60.0-9
- Bundling libffi for the sec-arches
- Added openssl-devel for the Python
- Fixing bundled gtk3

* Fri May 18 2018 Martin Stransky <stransky@redhat.com> - 60.0-8
- Added fix for mozilla BZ#1458492

* Wed May 16 2018 Martin Stransky <stransky@redhat.com> - 60.0-7
- Added patch from rhbz#1498561 to fix ppc64(le) crashes.

* Wed May 16 2018 Martin Stransky <stransky@redhat.com> - 60.0-6
- Disabled jemalloc on second arches

* Sun May  6 2018 Jan Horak <jhorak@redhat.com> - 60.0-4
- Update to 60.0 ESR

* Thu Mar  8 2018 Jan Horak <jhorak@redhat.com> - 52.7.0-1
- Update to 52.7.0 ESR

* Mon Jan 29 2018 Martin Stransky <stransky@redhat.com> - 52.6.0-2
- Build Firefox for desktop arches only (x86_64 and ppc64le)

* Thu Jan 18 2018 Martin Stransky <stransky@redhat.com> - 52.6.0-1
- Update to 52.6.0 ESR

* Thu Nov  9 2017 Jan Horak <jhorak@redhat.com> - 52.5.0-1
- Update to 52.5.0 ESR

* Mon Sep 25 2017 Jan Horak <jhorak@redhat.com> - 52.4.0-1
- Update to 52.4.0 ESR

* Thu Aug  3 2017 Jan Horak <jhorak@redhat.com> - 52.3.0-3
- Update to 52.3.0 ESR (b2)
- Require correct nss version

* Tue Jun 13 2017 Jan Horak <jhorak@redhat.com> - 52.2.0-1
- Update to 52.2.0 ESR

* Wed May 24 2017 Jan Horak <jhorak@redhat.com> - 52.1.2-1
- Update to 52.1.2 ESR

* Wed May 24 2017 Jan Horak <jhorak@redhat.com> - 52.0-7
- Added fix for accept language (rhbz#1454322)

* Wed Mar 22 2017 Jan Horak <jhorak@redhat.com> - 52.0-6
- Removing patch required for older NSS from RHEL 7.3
- Added patch for rhbz#1414564

* Fri Mar 17 2017 Martin Stransky <stransky@redhat.com> - 52.0-5
- Added fix for mozbz#1348168/CVE-2017-5428

* Mon Mar  6 2017 Jan Horak <jhorak@redhat.com> - 52.0-4
- Update to 52.0 ESR (b4)

* Thu Mar 2 2017 Martin Stransky <stransky@redhat.com> - 52.0-3
- Added fix for rhbz#1423012 - ppc64 gfx crashes

* Wed Mar  1 2017 Jan Horak <jhorak@redhat.com> - 52.0-2
- Enable system nss

* Tue Feb 28 2017 Martin Stransky <stransky@redhat.com> - 52.0-1
- Update to 52.0ESR (B1)
- Build RHEL7 package for Gtk3

* Mon Feb 27 2017 Martin Stransky <stransky@redhat.com> - 52.0-0.13
- Added fix for rhbz#1414535

* Tue Feb 21 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.12
- Update to 52.0b8

* Tue Feb  7 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.11
- Readded addons patch

* Mon Feb  6 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.10
- Update to 52.0b3

* Tue Jan 31 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.9
- Update to 52.0b2

* Fri Jan 27 2017 Jan Horak <jhorak@redhat.com> - 52.0-0.8
- Update to 52.0b1

* Thu Dec  8 2016 Jan Horak <jhorak@redhat.com> - 52.0-0.5
- Firefox Aurora 52 testing build
