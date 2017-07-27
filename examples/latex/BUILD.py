import os

from cook import core, latex, file, libreoffice, gimp

images = {}
for path in core.glob('dynamic/*'):
    if path.endswith('.odg'):
        image = libreoffice.convert(
            source=path,
            format='pdf'
        )
        images[os.path.basename(path)] = image.output
    elif path.endswith('.xcf'):
        image = gimp.export(
            source=path,
        )
        images[os.path.basename(path)] = image.output

templated = file.template(
    source='src/paper.tex',
    mapping=images
)

latex.document(
    source=templated.output,
    name='paper.pdf',
    contains=images.values(),
    texinputs=['static/']
)

# TODO: "Counter-resolve()" instead of basename (abs -> src-rel)
