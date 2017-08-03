from cook import misc

misc.run(
    inputs=['copy_me.txt'],
    outputs=['copied.txt'],
    command=['cp', '$INPUTS', '$OUTPUTS'],
    message='Doing that crazy copy stuff.'
)
