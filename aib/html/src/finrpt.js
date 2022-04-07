NS='http://www.w3.org/2000/svg';

function setup_finrpt(frame, ref, args) {
  var page = frame.page;
  page.style.padding = '0px';  // over-ride default padding

  var svg = document.createElementNS(NS, 'svg');
  page.appendChild(svg);
  svg.pos = frame.obj_list.length;
  frame.obj_list.push(svg);
  frame.form.obj_dict[ref] = svg;
  svg.frame = frame;
  svg.ref = ref;
  svg.help_msg = null;
  svg.tabIndex = 0;  // enable focus
  svg.style.outline = 'none';  // suppress outline on focus
  svg.active_frame = frame;

  for (var i=0, args_length=args.length; i<args_length; i++) {
    var elem = args[i];
    var [elem_type, elem_args] = elem;
    switch(elem_type) {
      case 'page':
        var view_wd = elem_args.width, view_ht = elem_args.height;
        if (view_ht > (max_h - 90)) {
          var svg_ht = (max_h - 90);  // adjust for header_row, toolbar
          var svg_wd = svg_ht / view_ht * view_wd;  // maintain aspect ratio
          }
        else {
          var svg_ht = view_ht, svg_wd = view_wd;
          };
        svg.wd = view_wd;
        svg.ht = view_ht;
        svg.setAttributeNS(null, 'width', svg_wd);
        svg.setAttributeNS(null, 'height', svg_ht);
        svg.setAttributeNS(null, 'viewBox', '0 0 ' + view_wd + ' ' + view_ht);
        svg.setAttributeNS(null, 'fill', 'none');
        break;
      case 'block':
        svg.block = {'x1': elem_args.x1, 'y1': elem_args.y1, 'x2': elem_args.x2, 'y2': elem_args.y2};
        break;
      case 'rect':
        var rect = document.createElementNS(NS, 'rect');
        svg.appendChild(rect);
        rect.setAttributeNS(null, 'x', elem_args.x);
        rect.setAttributeNS(null, 'y', elem_args.y);
        rect.setAttributeNS(null, 'width', elem_args.wd);
        rect.setAttributeNS(null, 'height', elem_args.ht);
        rect.setAttributeNS(null, 'stroke', elem_args.stroke);
        rect.setAttributeNS(null, 'stroke-width', elem_args.stroke_width);
        rect.setAttributeNS(null, 'fill', elem_args.fill);
        break;
      case 'font':
        svg.font = {'family': elem_args.family, 'weight': elem_args.weight, 'style': elem_args.style, 'size': elem_args.size};
        break;
      case 'text':
        var text = document.createElementNS(NS, 'text');
        svg.appendChild(text);
        text.textContent = elem_args.value;
        text.setAttributeNS(null, 'fill', elem_args.fill);
        if ('family' in elem_args) {
          text.setAttributeNS(null, 'font-family', elem_args.family)
          text.setAttributeNS(null, 'font-weight', elem_args.weight)
          text.setAttributeNS(null, 'font-style', elem_args.style);
          text.setAttributeNS(null, 'font-size', elem_args.size);
          }
        else {
          text.setAttributeNS(null, 'font-family', svg.font.family)
          text.setAttributeNS(null, 'font-weight', svg.font.weight)
          text.setAttributeNS(null, 'font-style', svg.font.style);
          text.setAttributeNS(null, 'font-size', svg.font.size);
          }
        var lng = text.getComputedTextLength();
        var ht = text.getExtentOfChar('x').height;
        if (elem_args.x === 'c') {  // centre
          var x = svg.block.x1 + ((svg.block.x2 - svg.block.x1) / 2) - (lng / 2);
          }
        else if (elem_args.x < 0) {  // right justified 0-x pixels from right margin
          var x = svg.block.x2 - lng + 1 + elem_args.x;
          }
        else {  // left justified x pixels from left margin
          var x = svg.block.x1 + elem_args.x;
          };
        var y = svg.block.y1 + elem_args.y;
        text.setAttributeNS(null, 'x', x);
        text.setAttributeNS(null, 'y', y);
        break;
      }
    }

  svg.onfocus = function() {
    got_focus(svg)
    }
  svg.got_focus = function() {
    return;
    }
  svg.lost_focus = function() {
    return true;
    }
  }
