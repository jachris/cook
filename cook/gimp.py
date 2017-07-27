import os

from . import core

_gimp = core.which('gimp')

_script = '''
from gimpfu import CLIP_TO_IMAGE

img = pdb.gimp_file_load('{input}', '{input}')
layer = pdb.gimp_image_merge_visible_layers(img, CLIP_TO_IMAGE)
pdb.gimp_file_save(img, layer, '{output}', '{output}')
pdb.gimp_image_delete(img)
pdb.gimp_quit(0)
'''


@core.rule
def export(source, destination=None, format='png'):
    if _gimp is None:
        raise FileNotFoundError('could not detect gimp')

    source = core.resolve(source)

    if destination is None:
        name = core.checksum(source) + '.' + format
        destination = core.intermediate(name)
    else:
        destination = core.build(destination)

    yield core.publish(
        inputs=[source, _gimp],
        outputs=[destination],
        message='Export XCF as "{}"'.format(destination),
        check=[format],
        result={
            'output': core.absolute(destination)
        }
    )

    command = [_gimp, '-indfs', '--batch-interpreter', 'python-fu-eval',
               '-b', _script.format(input=source, output=destination)]
    core.call(command, env=os.environ)
