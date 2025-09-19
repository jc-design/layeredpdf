#!/usr/bin/python

import inkex
import copy
import os
import subprocess
import pymupdf

from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Layer:
    id: str
    label: str
    svgfile: Path
    pdffile: Path

class LayeredPDFExport(inkex.Effect):
    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument('-o', '--output-dir',
                            type=Path,
                            default='~/',
                            help='Path to output directory')

    def effect(self):
        output_dir = self.options.output_dir
        if output_dir == "~":
            raise Exception(f'No output directory selected!')
        try:
            resolved_path = Path(output_dir).resolve(strict=True) # strict=True ensures the path exists
        except (FileNotFoundError, OSError):
            #inkex.utils.debug(f'Path {resolved_path} is not resolvable.')
            raise Exception(f'Path {output_dir} is not resolvable.')

        #inkex.utils.debug(output_dir)
        pdffilename = self.svg.name
        if len(pdffilename)==0:
            pdffilename = "layeredpdf"

        outpdf = pymupdf.open()

        layers = self.get_layers()
        for l in layers:
            #inkex.utils.debug(l.pdffile)
            self.export_to_svg(l)
            self.convert_svg_to_pdf(l)

            doc = pymupdf.open(l.pdffile) # open a document

            # Create a new overlay layer
            pdflayer = outpdf.add_ocg(l.label)

            for page in doc: # iterate the document pages
                if page.number+1 > outpdf.page_count:
                    outpage = outpdf.new_page(width=page.rect.width, height=page.rect.height)
                else:
                    outpage = outpdf[page.number]
                
                # insert input page into the correct rectangle
                outpage.show_pdf_page(
                    rect=outpage.rect,  # select output rect
                    docsrc=doc,  # input document
                    pno=page.number,
                    oc=pdflayer
                )  # input page numbe

        outpdf.save(os.path.join(self.options.output_dir, pdffilename + '.pdf'))
        outpdf.close()

    def convert_svg_to_pdf(self, layer: Layer):
        command = [
            'inkscape', str(layer.svgfile),
            '--export-area-page',
            '--export-dpi=96',
            '--export-type', 'pdf',
            '--export-filename', str(layer.pdffile),
        ] + list()

        try:
            subprocess.check_call(command)
        except Exception as e:
            raise Exception(f'Failed to convert {str(layer.svgfile)} to {str(layer.pdffile)}.\n{e}')  

    def export_to_svg(self, layer: Layer):
        doc = copy.deepcopy(self.document)

        xpath_query = '//svg:g[@inkscape:groupmode="layer"]'
        svg_layers = doc.xpath(xpath_query, namespaces=inkex.NSS)

        for l in svg_layers:
            if l.attrib['id'] in layer.id:
                l.attrib['style'] = 'display:inline'
            else:
                doc.getroot().remove(l)

        doc.write(str(layer.svgfile))   
    
    def get_layers(self) -> List[Layer]:
        
        xpath_query = '//svg:g[@inkscape:groupmode="layer"]'
        layer_xml_list = self.document.xpath(xpath_query, namespaces=inkex.NSS)

        layers = []

        for layer_xml in layer_xml_list:
            label_attrib_name = '{%s}label' % layer_xml.nsmap['inkscape']

            #if label_attrib_name not in group_xml.attrib:
            #   continue

            id = layer_xml.attrib['id']
            label = self.validate_layername(layer_xml.attrib[label_attrib_name])

            layers.append(Layer(id = id,
                                label = label,
                                svgfile = os.path.join(self.options.output_dir, label + '.svg'),
                                pdffile = os.path.join(self.options.output_dir, label + '.pdf')))

        return layers

    def validate_layername(self, filename: str) -> str:
        return ''.join(c for c in filename if c.isalnum() or c in "-_.() ")

if __name__ == '__main__':
    try:
        LayeredPDFExport().run(output=False)
    except Exception as e:
        inkex.utils.errormsg(e)
