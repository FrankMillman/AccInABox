import os.path
from subprocess import check_output, Popen, PIPE
import gzip
from base64 import b64encode as b64

def main():

    src_files = []
    for line in open('init.html'):
        if line.strip().startswith('<script'):
            start = line.find('src="')+5
            end = line[start:].find('"')+start
            src_files.append(line[start:end])

    with gzip.open('init.gz', 'wb') as fn:
        html = (
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"'
            ' "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">'
            '<html><head>'
            '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>'
            '<title>AccInABox</title>'
            )
        fn.write(html.encode('utf-8'))

        fn.write('<style type="text/css">'.encode('utf-8'))
    #   for root, dirs, files in os.walk('src'):
    #       for css in [css for css in files if css.endswith('.css')]:
    #           output = check_output(['python', 'cssmin.py', 'src/{0}'.format(css)])
    #           for line in output.split(b'\n'):
    #               fn.write(line)
        output = check_output(['python', 'cssmin.py', 'src/init.css'])
        for line in output.split(b'\n'):
            fn.write(line)
        fn.write('</style>'.encode('utf-8'))

        html = (
            '<h1>Welcome to AccInABox</h1>'
            '<br>'
            '<h2>Please wait ...</h2>'
            )
        fn.write(html.encode('utf-8'))

        html = (
            '<!--[if lt IE 9]><script type="text/javascript" src="excanvas.js">'
            '</script><![endif]-->'
            '<script type="text/javascript">'
            )
        fn.write(html.encode('utf-8'))

        for js in src_files:
                print(js)
                fd = open(js, 'rb')

                if js == 'src/images.js':
                    lines = []
                    for line in fd:
                        pos = line.find(b'src = ')
                        if pos == -1:
                            lines.append(line)
                        else:
                            """
                            iFirst_src = 'images/first.bmp';
                            """
                            pos += 6
                            new_line = []
                            new_line.append(line[:pos])
                            new_line.append(b"'data:image/bmp;base64,")
                            path = line[pos:].rstrip()[1:-2]  # strip ' and ;
                            src = open(path, 'rb').read()
                            new_line.append(b64(src))
                            new_line.append(b"';")
                            line = b''.join(new_line)
                            lines.append(line)
                    data = b'\n'.join(lines)
                else:
                    data = fd.read()

                p = Popen(['python', 'jsmin.py'], stdin=PIPE, stdout=PIPE)
                stdout,stderr = p.communicate(data)
                fn.write(stdout[1:])  # strip leading '\n'

        fn.write('</script>'.encode('utf-8'))

        html = '</head><body onload="on_load();"/></html>'
        fn.write(html.encode('utf-8'))
        fn.close()

if __name__ == '__main__':
    main()
