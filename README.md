## Layered PDF

LayereredPDF is i useful extention for [Inkscape](https://inkscape.org)

With the LayeredPDF extension, it is possible to create PDF documents with layers from within Inkscape. All layers from Inkscape are transferred 1:1 to the PDF.
To use these features, the PyMuPDF module must be installed.
<br><br>
I've tested it on Fedora Linux. It should work on Windows, too. Unfortunately on Windows I got an ModuleNotFound-Error, even PyMuPDF was correct installed.

**Edit**
Thanks to a kind reply from a user named Mark one can try following.
<br><br>
Since you can have different versions of python installed, you may nedd to specify the correct one in your preferences.
<br>
The only thing you need to do, is to add the path to the (correct) python executable that Inkscape should use in the extensions tag of the preferences.xml file (path found in Inkscape in Edit > Preferences > System > User Preferences) like so:<br>
`<group
     id="extensions"
     org.inkscape.output.png.inkscape.png_bitdepth="99"
     org.inkscape.output.png.inkscape.png_compression="6"
     org.inkscape.output.png.inkscape.png_antialias="2"
     python-interpreter="CORRECT_PATH_TO_PAYTHON\python.exe"
     org.inkscape.output.pdf.cairorenderer.PDFversion="PDF-1.5"
     org.inkscape.input.svg.scale="auto"
     jc-design.layeredpdf.output-dir="YOUR_OUTPUT_DIR" />
`
