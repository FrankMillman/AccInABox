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
  svg.nb_page = page.nb_page;

  for (var i=0, args_length=args.length; i<args_length; i++) {
    var elem = args[i];
    var [elem_type, elem_args] = elem;
    switch(elem_type) {
      case 'page':
        var view_wd = elem_args.width, view_ht = elem_args.height;
        if (view_ht > (max_h - 30)) {
          var svg_ht = (max_h - 30);  // adjust for header_row, toolbar
          var svg_wd = svg_ht / view_ht * view_wd;  // maintain aspect ratio
          }
        else {
          var svg_ht = view_ht, svg_wd = view_wd;
          };
        svg.wd = view_wd;
        svg.ht = view_ht;
        svg.x_pos = svg.y_pos = 0;
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
        if (elem_args.align === 'c')
          var x = (elem_args.x - (lng / 2));
        else if (elem_args.align === 'r')
          var x = (elem_args.x - lng);
        else
          var x = elem_args.x;
        var y = elem_args.y;
        text.setAttributeNS(null, 'x', x);
        text.setAttributeNS(null, 'y', y);

        if (elem_args.bkg !== undefined) {
          var rect = document.createElementNS(NS, 'rect');
          svg.insertBefore(rect, text);
          rect.setAttributeNS(null, 'x', elem_args.bkg_x1);
          rect.setAttributeNS(null, 'y', elem_args.bkg_y1);
          rect.setAttributeNS(null, 'width', elem_args.bkg_x2 - elem_args.bkg_x1);
          rect.setAttributeNS(null, 'height', elem_args.bkg_y2 - elem_args.bkg_y1);
          rect.setAttributeNS(null, 'fill', elem_args.bkg);
//          }
//        else {
//          var rect = document.createElementNS(NS, 'rect');
//          svg.insertBefore(rect, text);
//          rect.setAttributeNS(null, 'x', x);
//          rect.setAttributeNS(null, 'y', y-ht);
//          rect.setAttributeNS(null, 'width', lng);
//          rect.setAttributeNS(null, 'height', ht);
//          rect.setAttributeNS(null, 'fill', 'transparent');
//          text.rect = rect;
          };

        if (elem_args.cell_ref !== undefined) {
          text.cell_ref = elem_args.cell_ref;
          text.onmouseover = function() {
            this.style.cursor = 'pointer';
//            this.rect.setAttributeNS(null, 'fill', 'lightblue');
            this.style.textDecoration = 'underline';
            };
          text.onmouseleave = function() {
            this.style.cursor = 'default'
//            this.rect.setAttributeNS(null, 'fill', 'transparent');
            this.style.textDecoration = 'none';
            };
          text.onclick = function() {
            var args = [svg.ref, this.cell_ref];
            send_request('clicked', args);
            };
          };

        break;
      case 'underline':
        var path = document.createElementNS(NS,'path');
        svg.appendChild(path);
        var d = 'M' + elem_args.x1 + ',' + elem_args.y + ' H' + elem_args.x2
        if (elem_args.double === true)
          d += ' M' + elem_args.x1 + ',' + (elem_args.y+3) + ' H' + elem_args.x2;
        path.setAttributeNS(null, 'd', d);
        path.setAttributeNS(null, 'stroke', elem_args.colour);
        path.setAttributeNS(null, 'stroke-width', elem_args.width);
        break;
      case 'pagebreak':
        var path = document.createElementNS(NS,'path');
        svg.appendChild(path);
        var d = 'M0,' + (svg.ht * elem_args.pageno) + ' H' + svg.wd
        path.setAttributeNS(null, 'd', d);
        path.setAttributeNS(null, 'stroke', 'grey');
        path.setAttributeNS(null, 'stroke-width', 0.5);
        path.setAttributeNS(null, 'stroke-dasharray', '10, 10');
        break;
      }
    }

  svg.onkeydown = function(e) {
    if (e.code === 'ArrowUp') {
      if (svg.y_pos) {
        svg.y_pos -= ((svg.y_pos < 20) ? svg.y_pos : 20);
        svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
        };
      }
    else if (e.code === 'ArrowDown') {
      var bBox = svg.getBBox();
//      alert('bb=' + bBox.width + '/' + bBox.height + ' svg=' + svg.wd + '/' + svg.ht);
      var max_y = bBox.height - svg.ht + 29;  // why ' + 29' ? don't know, but it works
      var gap = Math.round(max_y) - svg.y_pos;
      if (gap) {
        svg.y_pos += ((gap < 20) ? gap : 20);
        svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
        };
      }
    else if (e.code === 'PageUp') {
      if (svg.y_pos) {
        svg.y_pos -= ((svg.y_pos < svg.ht) ? svg.y_pos : svg.ht);
        svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
        };
      }
    else if (e.code === 'PageDown') {
      var bBox = svg.getBBox();
      var max_y = bBox.height - svg.ht + 29;  // why ' + 29' ? don't know, but it works
      var gap = Math.round(max_y) - svg.y_pos;
      if (gap) {
        svg.y_pos += ((gap < svg.ht) ? gap : svg.ht);
        svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
        };
      }
    else if (e.code === 'ArrowLeft') {
      if (svg.x_pos) {
        svg.x_pos -= ((svg.x_pos < 20) ? svg.x_pos : 20);
        svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
        };
      }
    else if (e.code === 'ArrowRight') {
      var bBox = svg.getBBox();
      var max_x = bBox.width - svg.wd + 29;  // why ' + 29' ? don't know, but it works
      var gap = Math.round(max_x) - svg.x_pos;
      if (gap) {
        svg.x_pos += ((gap < 20) ? gap : 20);
        svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
        };
      }
    else if (e.code === 'NumpadAdd') {  // zoom in
      var ratio = svg.wd / svg.ht;
      svg.ht -= 20;
      svg.wd -= (20 * ratio);
      svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
      }
    else if (e.code === 'NumpadSubtract') {  // zoom out
      var ratio = svg.wd / svg.ht;
      svg.ht += 20;
      svg.wd += (20 * ratio);
      svg.setAttributeNS(null, 'viewBox', svg.x_pos + ' ' + svg.y_pos + ' ' + svg.wd + ' ' + svg.ht);
      };
    };
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
