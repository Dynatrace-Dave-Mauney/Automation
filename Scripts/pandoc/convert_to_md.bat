@echo off
rem Example Word to markdown script leveraging pandoc.
rem Copy to the directory where the Word document resides
rem The markdown file will be created in the same directory
\tools\pandoc-3.8.3\pandoc.exe DynatraceNamingStandards.docx -o DynatraceNamingStandards.md
@echo When notepad opens the markdown version:
@echo Change view to Markdown/Syntax
@echo Copy the entire document to buffer
@echo Edit the Launchpad: "Dynatrace Naming Standards" 
@echo Launchpad Link: https://xxxxxxxx.apps.dynatrace.com/ui/apps/dynatrace.launcher/launchpad/ccec6392-fd72-4088-b206-97c1f92907c0
@echo Hit "Configure" and then paste the markdown into the tile
@echo Notepad will start after you hit any key...
pause
notepad DynatraceNamingStandards.md

