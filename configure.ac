#                                               -*- Autoconf -*-
# Process this file with ./autogen.sh to produce a configure script

AC_PREREQ([2.68])
AC_INIT([smake], [0.01], [sadjad@cs.stanford.edu])
AM_INIT_AUTOMAKE([foreign])
AC_CONFIG_HEADERS([config.h])
AC_CONFIG_MACRO_DIRS([m4])

# Add C++ flags
CXX14_FLAGS="-std=c++14 -pthread"
PICKY_CXXFLAGS="-Wall -Wpedantic -Wextra -Weffc++ -Werror"
AC_SUBST([CXX14_FLAGS])
AC_SUBST([PICKY_CXXFLAGS])

# Checks for programs.
AC_PROG_CXX
LT_INIT

# Checks for libraries.
PKG_CHECK_MODULES([OpenSSL], [libssl libcrypto])

# Checks for header files.

# Checks for typedefs, structures, and compiler characteristics.

# Checks for library functions.

# Check for Python
AM_PATH_PYTHON(2.7)

AC_CONFIG_FILES([
	Makefile
	src/Makefile
	src/util/Makefile
	src/net/Makefile
	src/http/Makefile
	src/lambdareq/Makefile
	src/launch/Makefile
	src/pylaunch/Makefile])

AC_OUTPUT
