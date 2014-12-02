FROM opensuse:13.2

MAINTAINER Uwe L. Korn "uwelk@xhochy.com"

# make sure the repositories are up to date
RUN zypper --non-interactive --gpg-auto-import-keys ref
# Install system updates
RUN zypper --non-interactive update

# First install autoconf (required by automake)
RUN zypper install -y autoconf

# Install automake from Tumbleweed, version in 13.2 is too old
# TODO: Remove once we update to a newer OpenSuSE
ADD automake-1.14.1-56.1.noarch.rpm /
RUN rpm -i automake-1.14.1-56.1.noarch.rpm

# Add win32 repo
RUN zypper --non-interactive ar http://download.opensuse.org/repositories/windows:/mingw:/win32/openSUSE_13.1/windows:mingw:win32.repo
# make sure the repositories are up to date
RUN zypper --non-interactive --gpg-auto-import-keys ref
# Install system updates
RUN zypper --non-interactive update

# Install build system dev tools
RUN zypper install -y cmake git gcc-c++ wget tar patch libtool yasm pkg-config ragel unzip gettext-tools
# Install host system build tools
RUN zypper install -y mingw32-cross-gcc mingw32-cross-gcc-c++ mingw32-pkg-config mingw32-libtool

# Import the sources. We do not git clone here always as this takes very long
# and we would not be able to add custom modifications.
ADD vlc /vlc

WORKDIR /vlc/extras/tools
RUN ./bootstrap
RUN make

RUN mkdir /vlc/contrib/win32
WORKDIR /vlc/contrib/win32
# Pull the following dependencies from the mingw repository as we use them also
# in Tomahawk directly:
# * gnutls
# * taglib
# The following dependencies are disabled as we do not need them for tomahawk:
# * bluray
# * cddb
# * dvdread
# * dvdnav
# * regex
# * ssh2
# * vncserver
# Temporarily deactivated (we want to use them in the future):
# * projectM
# * glew
# Activated but should be deactivated:
# * gcrypt (used also in jreen)
# * gpg-error (used also in jreen)
# * taglib (used directly in tomahawk)
# * gnutls (used directly in tomahawk)
RUN ../bootstrap --host=i686-w64-mingw32 --disable-bluray --disable-cddb --disable-regex --disable-ssh2 --disable-vncserver --disable-dvdnav --disable-dvdread --disable-qt --disable-glew --disable-projectM
RUN make

WORKDIR /vlc
RUN ./bootstrap

RUN mkdir /vlc/win32
WORKDIR /vlc/win32
# Install dependencies that we also use in Tomahawk
# TODO
# FIXME: vpx currently disabled as it is not building, reenable for youtube support
RUN ../configure --host=i686-w64-mingw32 --disable-lua --disable-vpx
RUN make
RUN make install
