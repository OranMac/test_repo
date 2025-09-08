NAME := firefox
SPECFILE := $(NAME).spec

define find-common
if [ -f ../common/Makefile.common ] ; then \
	if [ -f ../common/CVS/Root -a -w ../common/Makefile.common ] ; then cd ../common ; cvs -Q update ; fi ; echo "../common" ; fi
endef

COMMON_DIR := $(shell $(find-common))

ifeq ($(COMMON_DIR),)
define checkout-common
test -f CVS/Root && { cvs -Q -d $$(cat CVS/Root) checkout common && mv common ../common && echo "../common" ; } || { echo "ERROR: I can't figure out how to checkout the 'common' module." ; exit -1 ; } >&2
endef
COMMON_DIR := $(shell $(checkout-common))
endif

include $(COMMON_DIR)/Makefile.common
