from flake8_rst.rst import find_sourcecode


def test_python(result_dir, sourcecode_python):
    with open(sourcecode_python) as f:
        result = list(find_sourcecode(f.read()))

    result_file = result_dir / f'{sourcecode_python.name}.py'
    with open(result_file, 'w') as f:
        for i, (code, indent, line_number) in enumerate(result):
            if i:
                f.write('\n')
            f.write(f'# line number: {line_number}\n')
            f.write(f'# indent: {indent}\n')
            f.write(code)
            f.write('\n# end of block\n')
        f.write('\n')

    assert result
