# main Makefile calling other Makefiles

# dependencies for a chapter
MDFILES := $(wildcard ./*.mdfiles)
MDBASENAMES := $(basename $(MDFILES))

MDDIRS := $(dir $(MDFILES))

# pdf:
# 	@echo "Processing markdown files to PDF:"
# 		for file in $(MDFILES); \
# 		do \
# 			echo "------------" \
# 			echo $$file ; \
# 			echo $(MAKE) -f Makefile.md2pdf -n pdf REPORT=`basename $$file`  ; \
# 			$(MAKE) -f Makefile.md2pdf -n pdf REPORT=`basename $$file`  ; \
# 		done

pdf:
	@echo "Processing markdown files to PDF:"
		for file in $(MDFILES); \
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
		for file in $(MDFILES); \
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
		for file in $(MDFILES); \
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
	@echo "MDFILES = "$(MDFILES)
	@echo "MDDIRS = "$(MDDIRS)
	@echo "MDBASENAMES = "$(MDBASENAMES)
