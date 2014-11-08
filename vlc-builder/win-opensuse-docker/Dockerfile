FROM opensuse:13.1

MAINTAINER Uwe L. Korn "uwelk@xhochy.com"

# Add win32 repo
RUN zypper --non-interactive ar http://download.opensuse.org/repositories/windows:/mingw:/win32/openSUSE_13.1/windows:mingw:win32.repo
# make sure the repositories are up to date
RUN zypper --non-interactive --gpg-auto-import-keys ref
# Install system updates
RUN zypper --non-interactive update

# Install build system dev tools
RUN zypper install -y cmake git gcc-c++ wget tar patch autoconf automake libtool yasm pkg-config ragel unzip gettext-tools
# Install host system build tools
RUN zypper install -y mingw32-cross-gcc mingw32-cross-gcc-c++ mingw32-pkg-config mingw32-libtool

# Import the sources. We do not git clone here always as this takes very long
# and we would not be able to add custom modifications.
ADD vlc-2.2 /vlc-2.2

RUN mkdir /vlc-2.2/contrib/win32
WORKDIR /vlc-2.2/contrib/win32
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
RUN ../bootstrap --host=i686-w64-mingw32 --disable-gnutls --disable-taglib --disable-bluray --disable-cddb --disable-regex --disable-ssh2 --disable-gcrypt --disable-gpg-error --disable-vncserver --disable-dvdnav --disable-dvdread --disable-qt --disable-glew --disable-projectM
RUN make

WORKDIR /vlc-2.2
RUN ./bootstrap

RUN mkdir /vlc-2.2/win32
WORKDIR /vlc-2.2/win32
# Install dependencies that we also use in Tomahawk
RUN zypper install -y mingw32-gnutls mingw32-taglib
# RUN ../configure --host=i686-w64-mingw32 --disable-lua
# #RUN ../configure --enable-update-check --enable-lua --enable-faad --enable-flac --enable-theora --enable-twolame --enable-quicktime --enable-avcodec --enable-merge-ffmpeg --enable-dca --enable-mpc --disable-libass --enable-x264 --enable-schroedinger --enable-realrtsp --enable-live555 --disable-dvdread --enable-shout --enable-goom --disable-caca --disable-sdl --disable-qt --disable-skins2 --enable-sse --enable-mmx --disable-libcddb --enable-zvbi --disable-telx --disable-freetype --host=i686-w64-mingw32
