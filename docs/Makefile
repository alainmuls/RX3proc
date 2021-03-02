# main Makefile calling other Makefiles

# dependencies for a chapter
MDFILE := $(wildcard ./*.mdfiles)
MDBASENAMES := $(basename $(MDFILE))

MDDIRS := $(dir $(MDFILE))
MD_FILES=$(shell cat $(MDFILE))

# pdf:
# 	@echo "Processing markdown files to PDF:"
# 		for file in $(MDFILE); \
# 		do \
# 			echo "------------" \
# 			echo $$file ; \
# 			echo $(MAKE) -f Makefile.md2pdf -n pdf REPORT=`basename $$file`  ; \
# 			$(MAKE) -f Makefile.md2pdf -n pdf REPORT=`basename $$file`  ; \
# 		done

pdf:
	@echo "Processing markdown files to PDF:"
		for file in $(MDFILE); \
		do \
			echo "------------" ; \
			echo `tput setaf 2` ; \
			echo $$file ; \
			echo `tput sgr0` ; \
			echo $(MAKE) -f Makefile.md2pdf pdf REPORT=$$file  ; \
			$(MAKE) -f Makefile.md2pdf pdf REPORT=$$file  ; \
		done

docx:
	@echo "Processing markdown files to DOCX:"
		for file in $(MDFILE); \
		do \
			echo "------------" ; \
			echo `tput setaf 2` ; \
			echo $$file ; \
			echo `tput sgr0` ; \
			echo $(MAKE) -f Makefile.md2pdf docx REPORT=$$file  ; \
			$(MAKE) -f Makefile.md2pdf docx REPORT=$$file  ; \
		done

html:
	@echo "Processing markdown files to HTML:"
		for file in $(MDFILE); \
		do \
			echo "------------" ; \
			echo `tput setaf 2` ; \
			echo $$file ; \
			echo `tput sgr0` ; \
			echo $(MAKE) -f Makefile.md2pdf html REPORT=$$file  ; \
			$(MAKE) -f Makefile.md2pdf html REPORT=$$file  ; \
		done

clean:
	@echo "Cleaning up markdown files:"
		for file in $(MDBASENAMES); \
		do \
			echo "------------" ; \
			echo `tput setaf 2` ; \
			echo $$file ; \
			echo `tput sgr0` ; \
			echo $(MAKE) -f Makefile.md2pdf clean REPORT=$$file ; \
			$(MAKE) -f Makefile.md2pdf clean REPORT=$$file ; \
		done

files:
	@echo "MDFILE = "$(MDFILE)
	@echo "MDDIRS = "$(MDDIRS)
	@echo "MDBASENAMES = "$(MDBASENAMES)
	@echo "MD_FILES = "$(MD_FILES)
